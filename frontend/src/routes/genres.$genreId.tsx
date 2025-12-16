import { createFileRoute, Link } from '@tanstack/react-router';
import { useState } from 'react';
import {
  useGenerateGospel,
  useGenerateJazz,
  useGenerateBlues,
  useGenerateNeosoul,
  useGenerateClassical,
  useGenerateReggae,
  useGenerateLatin,
  useGenerateRnB,
} from '../hooks/useGenre';

export const Route = createFileRoute('/genres/$genreId')({
  component: GenreDetailPage,
});

const genreInfo: Record<string, any> = {
  gospel: {
    name: 'Gospel',
    icon: '🙏',
    color: 'from-purple-500 to-pink-500',
    description: 'Generate contemporary gospel piano arrangements with rich harmonies and dynamic voicings',
  },
  jazz: {
    name: 'Jazz',
    icon: '🎷',
    color: 'from-blue-500 to-cyan-500',
    description: 'Create jazz piano arrangements with bebop, modal, and contemporary styles',
  },
  blues: {
    name: 'Blues',
    icon: '🎸',
    color: 'from-indigo-500 to-purple-500',
    description: 'Generate authentic blues progressions with Chicago, Delta, and jump blues styles',
  },
  neosoul: {
    name: 'Neo-Soul',
    icon: '✨',
    color: 'from-pink-500 to-rose-500',
    description: 'Create smooth neo-soul chord progressions with jazzy, lush voicings',
  },
  classical: {
    name: 'Classical',
    icon: '🎹',
    color: 'from-amber-500 to-orange-500',
    description: 'Generate classical piano pieces in various historical periods and forms',
  },
  reggae: {
    name: 'Reggae',
    icon: '🌴',
    color: 'from-green-500 to-emerald-500',
    description: 'Create authentic reggae piano parts with roots, dancehall, and lovers rock styles',
  },
  latin: {
    name: 'Latin',
    icon: '🎺',
    color: 'from-red-500 to-orange-500',
    description: 'Generate Latin piano arrangements with salsa, bossa nova, samba, and cha-cha rhythms',
  },
  rnb: {
    name: 'R&B',
    icon: '🎤',
    color: 'from-violet-500 to-fuchsia-500',
    description: 'Create R&B piano progressions spanning classic, neo, and contemporary eras',
  },
};

function GenreDetailPage() {
  const { genreId } = Route.useParams();
  const genre = genreInfo[genreId];

  const [generatedFile, setGeneratedFile] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Hook selection based on genre
  const generateGospel = useGenerateGospel();
  const generateJazz = useGenerateJazz();
  const generateBlues = useGenerateBlues();
  const generateNeosoul = useGenerateNeosoul();
  const generateClassical = useGenerateClassical();
  const generateReggae = useGenerateReggae();
  const generateLatin = useGenerateLatin();
  const generateRnB = useGenerateRnB();

  if (!genre) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h2 className="text-2xl font-bold mb-2">Genre not found</h2>
        <Link to="/genres" className="text-blue-600 hover:underline">
          Back to genres
        </Link>
      </div>
    );
  }

  const handleGenerate = async (params: any) => {
    try {
      setError(null);
      setGeneratedFile(null);

      let response;
      switch (genreId) {
        case 'gospel':
          response = await generateGospel.mutateAsync(params);
          break;
        case 'jazz':
          response = await generateJazz.mutateAsync(params);
          break;
        case 'blues':
          response = await generateBlues.mutateAsync(params);
          break;
        case 'neosoul':
          response = await generateNeosoul.mutateAsync(params);
          break;
        case 'classical':
          response = await generateClassical.mutateAsync(params);
          break;
        case 'reggae':
          response = await generateReggae.mutateAsync(params);
          break;
        case 'latin':
          response = await generateLatin.mutateAsync(params);
          break;
        case 'rnb':
          response = await generateRnB.mutateAsync(params);
          break;
      }

      if (response?.midi_file_path) {
        setGeneratedFile(response.midi_file_path);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generation failed');
    }
  };

  const isGenerating =
    generateGospel.isPending ||
    generateJazz.isPending ||
    generateBlues.isPending ||
    generateNeosoul.isPending ||
    generateClassical.isPending ||
    generateReggae.isPending ||
    generateLatin.isPending ||
    generateRnB.isPending;

  return (
    <div className="container mx-auto px-4 py-8">
      <Link
        to="/genres"
        className="text-blue-600 hover:underline mb-4 inline-block"
      >
        ← Back to genres
      </Link>

      {/* Header */}
      <div className={`bg-gradient-to-br ${genre.color} rounded-lg p-8 mb-8 text-white`}>
        <div className="text-5xl mb-4">{genre.icon}</div>
        <h1 className="text-4xl font-bold mb-2">{genre.name} Generator</h1>
        <p className="text-lg opacity-90">{genre.description}</p>
      </div>

      {/* Generator Form */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
        <h2 className="text-2xl font-bold mb-4">Generate {genre.name}</h2>

        {genreId === 'gospel' && (
          <GospelForm onGenerate={handleGenerate} isGenerating={isGenerating} />
        )}
        {genreId === 'jazz' && (
          <JazzForm onGenerate={handleGenerate} isGenerating={isGenerating} />
        )}
        {/* Add other genre-specific forms as needed */}
        {!['gospel', 'jazz'].includes(genreId) && (
          <div className="text-center py-8 text-gray-500">
            <p>Generator form coming soon for {genre.name}</p>
          </div>
        )}

        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            {error}
          </div>
        )}

        {generatedFile && (
          <div className="mt-4 bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-green-800 font-medium mb-2">✓ Generated successfully!</p>
            <a
              href={generatedFile}
              download
              className="inline-block bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
            >
              Download MIDI
            </a>
          </div>
        )}
      </div>
    </div>
  );
}

// Gospel-specific form
function GospelForm({
  onGenerate,
  isGenerating,
}: {
  onGenerate: (params: any) => void;
  isGenerating: boolean;
}) {
  const [description, setDescription] = useState('Kirk Franklin style uptempo in C major');
  const [tempo, setTempo] = useState(138);
  const [numBars, setNumBars] = useState(16);

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-2">Description</label>
        <input
          type="text"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          placeholder="Describe the style and mood..."
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Tempo (BPM)</label>
          <input
            type="number"
            value={tempo}
            onChange={(e) => setTempo(Number(e.target.value))}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Number of Bars</label>
          <input
            type="number"
            value={numBars}
            onChange={(e) => setNumBars(Number(e.target.value))}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
          />
        </div>
      </div>
      <button
        onClick={() =>
          onGenerate({
            description,
            tempo,
            num_bars: numBars,
            application: 'uptempo',
            ai_percentage: 0.0,
          })
        }
        disabled={isGenerating}
        className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50"
      >
        {isGenerating ? 'Generating...' : 'Generate Gospel Arrangement'}
      </button>
    </div>
  );
}

// Jazz-specific form
function JazzForm({
  onGenerate,
  isGenerating,
}: {
  onGenerate: (params: any) => void;
  isGenerating: boolean;
}) {
  return (
    <div className="text-center py-8 text-gray-500">
      <p>Jazz generator form coming soon</p>
    </div>
  );
}
