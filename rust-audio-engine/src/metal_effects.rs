//! Metal GPU Effects Processor for M4 MacBook Pro
//!
//! Uses Metal compute shaders for:
//! - Convolution reverb
//! - EQ
//! - Mixing
//! - Real-time audio processing

use anyhow::{Context, Result};
use metal::*;
use core_foundation::base::TCFType;
use std::mem;

pub struct MetalEffectsProcessor {
    device: Device,
    command_queue: CommandQueue,
    reverb_pipeline: Option<ComputePipelineState>,
}

impl MetalEffectsProcessor {
    /// Create a new Metal effects processor
    pub fn new() -> Result<Self> {
        // Get default Metal device (M4 GPU)
        let device = Device::system_default()
            .context("No Metal device found (M4 GPU should be available)")?;

        let command_queue = device.new_command_queue();

        println!("Metal GPU initialized: {}", device.name());
        println!("  Max threads per threadgroup: {:?}",
                 device.max_threads_per_threadgroup());

        let mut processor = Self {
            device,
            command_queue,
            reverb_pipeline: None,
        };

        // Compile reverb shader on initialization
        processor.compile_reverb_shader()?;

        Ok(processor)
    }

    /// Process audio samples with GPU effects
    pub fn process(&mut self, samples: &[f32], enable_reverb: bool) -> Result<Vec<f32>> {
        if !enable_reverb {
            // No processing, return copy
            return Ok(samples.to_vec());
        }

        // Apply GPU reverb
        self.apply_reverb_gpu(samples)
    }

    /// Apply convolution reverb using Metal GPU
    fn apply_reverb_gpu(&mut self, samples: &[f32]) -> Result<Vec<f32>> {
        // Try GPU processing first, fallback to CPU if needed
        if let Some(pipeline) = &self.reverb_pipeline {
            self.apply_reverb_gpu_impl(samples, pipeline)
                .or_else(|e| {
                    eprintln!("GPU reverb failed, falling back to CPU: {}", e);
                    self.apply_reverb_cpu(samples)
                })
        } else {
            // No pipeline available, use CPU
            self.apply_reverb_cpu(samples)
        }
    }

    /// GPU implementation of algorithmic reverb
    fn apply_reverb_gpu_impl(&self, samples: &[f32], pipeline: &ComputePipelineState) -> Result<Vec<f32>> {
        // Create a simple impulse response for convolution
        // This simulates a small room reverb
        let impulse_length = 4410; // 100ms at 44.1kHz
        let mut impulse = vec![0.0f32; impulse_length];

        // Generate exponentially decaying impulse response
        for i in 0..impulse_length {
            let t = i as f32 / impulse_length as f32;
            impulse[i] = (-t * 5.0).exp() * (1.0 - t) * 0.3; // 30% wet mix
        }

        // Create Metal buffers
        let input_buffer = create_buffer_from_slice(&self.device, samples);
        let impulse_buffer = create_buffer_from_slice(&self.device, &impulse);

        let output_length = samples.len();
        let output_buffer = self.device.new_buffer(
            (output_length * mem::size_of::<f32>()) as u64,
            MTLResourceOptions::StorageModeShared
        );

        let input_len = samples.len() as u32;
        let impulse_len = impulse.len() as u32;
        let input_len_buffer = create_buffer_from_slice(&self.device, &[input_len]);
        let impulse_len_buffer = create_buffer_from_slice(&self.device, &[impulse_len]);

        // Create command buffer and encoder
        let command_buffer = self.command_queue.new_command_buffer();
        let encoder = command_buffer.new_compute_command_encoder();

        encoder.set_compute_pipeline_state(pipeline);
        encoder.set_buffer(0, Some(&input_buffer), 0);
        encoder.set_buffer(1, Some(&impulse_buffer), 0);
        encoder.set_buffer(2, Some(&output_buffer), 0);
        encoder.set_buffer(3, Some(&input_len_buffer), 0);
        encoder.set_buffer(4, Some(&impulse_len_buffer), 0);

        // Calculate thread groups
        let thread_group_size = MTLSize {
            width: pipeline.max_total_threads_per_threadgroup().min(256),
            height: 1,
            depth: 1,
        };

        let thread_groups = MTLSize {
            width: (output_length as u64 + thread_group_size.width - 1) / thread_group_size.width,
            height: 1,
            depth: 1,
        };

        encoder.dispatch_thread_groups(thread_groups, thread_group_size);
        encoder.end_encoding();

        // Execute and wait
        command_buffer.commit();
        command_buffer.wait_until_completed();

        // Read results
        let mut output = vec![0.0f32; output_length];
        unsafe {
            let ptr = output_buffer.contents() as *const f32;
            std::ptr::copy_nonoverlapping(ptr, output.as_mut_ptr(), output_length);
        }

        Ok(output)
    }

    /// Simple CPU-based reverb (fallback)
    fn apply_reverb_cpu(&self, samples: &[f32]) -> Result<Vec<f32>> {
        let mut output = samples.to_vec();

        // Simple algorithmic reverb (Freeverb-style)
        const DELAY_SAMPLES: &[usize] = &[
            1557, 1617, 1491, 1422, 1277, 1356, 1188, 1116
        ];

        let delay_count = DELAY_SAMPLES.len();
        let mut delay_buffers: Vec<Vec<f32>> = DELAY_SAMPLES
            .iter()
            .map(|&size| vec![0.0; size])
            .collect();

        let mut delay_indices = vec![0usize; delay_count];

        const FEEDBACK: f32 = 0.5;
        const WET: f32 = 0.2;  // 20% reverb
        const DRY: f32 = 0.8;  // 80% dry signal

        for i in 0..samples.len() {
            let input = samples[i];
            let mut reverb = 0.0;

            // Process all delay lines (comb filters)
            for j in 0..delay_count {
                let delay_size = DELAY_SAMPLES[j];
                let delay_idx = delay_indices[j];

                // Read from delay buffer
                let delayed = delay_buffers[j][delay_idx];
                reverb += delayed;

                // Write to delay buffer with feedback
                delay_buffers[j][delay_idx] = input + delayed * FEEDBACK;

                // Update delay index
                delay_indices[j] = (delay_idx + 1) % delay_size;
            }

            // Mix dry and wet signals
            reverb /= delay_count as f32;
            output[i] = input * DRY + reverb * WET;
        }

        Ok(output)
    }

    /// Compile Metal shader for GPU reverb
    fn compile_reverb_shader(&mut self) -> Result<()> {
        let shader_source = r#"
            #include <metal_stdlib>
            using namespace metal;

            // Convolution reverb kernel
            kernel void convolve_reverb(
                device const float* input [[buffer(0)]],
                device const float* impulse [[buffer(1)]],
                device float* output [[buffer(2)]],
                constant uint& input_length [[buffer(3)]],
                constant uint& impulse_length [[buffer(4)]],
                uint id [[thread_position_in_grid]]
            ) {
                if (id >= input_length) return;

                float sum = 0.0;
                for (uint i = 0; i < impulse_length && i <= id; i++) {
                    sum += input[id - i] * impulse[i];
                }

                output[id] = sum;
            }
        "#;

        let library = self.device
            .new_library_with_source(shader_source, &CompileOptions::new())
            .map_err(|e| anyhow::anyhow!("Failed to compile Metal shader: {}", e))?;

        let kernel = library
            .get_function("convolve_reverb", None)
            .map_err(|_| anyhow::anyhow!("Failed to get kernel function"))?;

        let pipeline = self.device
            .new_compute_pipeline_state_with_function(&kernel)
            .map_err(|e| anyhow::anyhow!("Failed to create pipeline state: {}", e))?;

        self.reverb_pipeline = Some(pipeline);
        println!("Metal reverb shader compiled successfully");

        Ok(())
    }
}

/// Helper to create Metal buffer from slice
fn create_buffer_from_slice<T>(device: &Device, data: &[T]) -> Buffer {
    let byte_length = (data.len() * mem::size_of::<T>()) as u64;
    let buffer = device.new_buffer(byte_length, MTLResourceOptions::StorageModeShared);

    unsafe {
        let ptr = buffer.contents() as *mut T;
        std::ptr::copy_nonoverlapping(data.as_ptr(), ptr, data.len());
    }

    buffer
}
