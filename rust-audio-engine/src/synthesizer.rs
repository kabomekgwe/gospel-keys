//! MIDI Synthesizer using rustysynth
//!
//! Converts MIDI files to audio samples using SoundFont synthesis

use anyhow::{Context, Result};
use midly::{Smf, TrackEventKind, MidiMessage};
use rustysynth::{SoundFont, Synthesizer, SynthesizerSettings};
use std::fs::File;
use std::sync::Arc;

pub struct MidiSynthesizer {
    synthesizer: Synthesizer,
    sample_rate: u32,
}

impl MidiSynthesizer {
    /// Create a new MIDI synthesizer with a SoundFont
    pub fn new(soundfont_path: &str, sample_rate: u32) -> Result<Self> {
        // Load SoundFont
        let mut sf2_file = File::open(soundfont_path)
            .context("Failed to open SoundFont file")?;

        let sound_font = Arc::new(
            SoundFont::new(&mut sf2_file)
                .context("Failed to load SoundFont")?
        );

        // Create synthesizer settings
        let settings = SynthesizerSettings::new(sample_rate as i32);

        // Create synthesizer
        let synthesizer = Synthesizer::new(&sound_font, &settings)
            .context("Failed to create synthesizer")?;

        Ok(Self {
            synthesizer,
            sample_rate,
        })
    }

    /// Synthesize a MIDI file to audio samples
    pub fn synthesize_file(&mut self, midi_path: &str) -> Result<Vec<f32>> {
        // Parse MIDI file
        let midi_data = std::fs::read(midi_path)
            .context("Failed to read MIDI file")?;

        let smf = Smf::parse(&midi_data)
            .context("Failed to parse MIDI file")?;

        // Convert timing to real-time
        let ticks_per_beat = match smf.header.timing {
            midly::Timing::Metrical(tpb) => tpb.as_int() as f64,
            midly::Timing::Timecode(fps, tpf) => {
                (fps.as_f32() * tpf as f32) as f64
            }
        };

        let mut tempo = 500_000.0; // Default: 120 BPM (500,000 microseconds per beat)
        let mut events = Vec::new();

        // Collect all events with absolute timing
        for track in smf.tracks {
            let mut current_tick = 0u64;

            for event in track {
                current_tick += event.delta.as_int() as u64;

                match event.kind {
                    TrackEventKind::Midi { channel, message } => {
                        let time_seconds = (current_tick as f64 * tempo) /
                                         (ticks_per_beat * 1_000_000.0);

                        events.push((time_seconds, channel.as_int(), message));
                    }
                    TrackEventKind::Meta(midly::MetaMessage::Tempo(t)) => {
                        tempo = t.as_int() as f64;
                    }
                    _ => {}
                }
            }
        }

        // Sort events by time
        events.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());

        // Calculate total duration
        let total_duration = events.last()
            .map(|(t, _, _)| *t)
            .unwrap_or(0.0) + 1.0; // Add 1 second padding

        let total_samples = (total_duration * self.sample_rate as f64) as usize;

        // Prepare output buffer (stereo: left and right channels)
        let mut left = vec![0.0f32; total_samples];
        let mut right = vec![0.0f32; total_samples];

        // Process events in chunks for better performance
        let chunk_size = self.sample_rate as usize; // 1 second chunks
        let mut current_sample = 0;
        let mut event_index = 0;

        while current_sample < total_samples {
            let chunk_end = (current_sample + chunk_size).min(total_samples);
            let chunk_time_start = current_sample as f64 / self.sample_rate as f64;
            let chunk_time_end = chunk_end as f64 / self.sample_rate as f64;

            // Process all events in this time chunk
            while event_index < events.len() {
                let (event_time, channel, message) = &events[event_index];

                if *event_time >= chunk_time_end {
                    break;
                }

                // Send MIDI message to synthesizer
                self.process_midi_message(*channel, message);
                event_index += 1;
            }

            // Render audio for this chunk
            let chunk_len = chunk_end - current_sample;
            let left_chunk = &mut left[current_sample..chunk_end];
            let right_chunk = &mut right[current_sample..chunk_end];

            self.synthesizer.render(left_chunk, right_chunk);

            current_sample = chunk_end;
        }

        // Interleave stereo channels
        let mut interleaved = Vec::with_capacity(total_samples * 2);
        for i in 0..total_samples {
            interleaved.push(left[i]);
            interleaved.push(right[i]);
        }

        Ok(interleaved)
    }

    /// Process a single MIDI message
    fn process_midi_message(&mut self, channel: u8, message: &MidiMessage) {
        match message {
            MidiMessage::NoteOn { key, vel } => {
                if vel.as_int() > 0 {
                    self.synthesizer.note_on(
                        channel as i32,
                        key.as_int() as i32,
                        vel.as_int() as i32,
                    );
                } else {
                    // Velocity 0 is same as note off
                    self.synthesizer.note_off(channel as i32, key.as_int() as i32);
                }
            }
            MidiMessage::NoteOff { key, .. } => {
                self.synthesizer.note_off(channel as i32, key.as_int() as i32);
            }
            MidiMessage::ProgramChange { program } => {
                self.synthesizer.process_midi_message(
                    channel as i32,
                    0xC0, // Program change
                    program.as_int() as i32,
                    0,
                );
            }
            MidiMessage::Controller { controller, value } => {
                self.synthesizer.process_midi_message(
                    channel as i32,
                    0xB0, // Control change
                    controller.as_int() as i32,
                    value.as_int() as i32,
                );
            }
            MidiMessage::PitchBend { bend } => {
                let value = bend.as_int();
                self.synthesizer.process_midi_message(
                    channel as i32,
                    0xE0, // Pitch bend
                    value as i32 & 0x7F,
                    (value as i32 >> 7) & 0x7F,
                );
            }
            _ => {}
        }
    }
}
