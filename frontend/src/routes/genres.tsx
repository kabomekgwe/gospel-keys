import { createFileRoute, Link } from '@tanstack/react-router';
import { GENRES } from '@/lib/genres';

export const Route = createFileRoute('/genres')({
  component: GenresPage,
});

function GenresPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Music Genres</h1>
        <p className="text-gray-600 text-lg">
          Explore and generate music across 8 different genres powered by AI
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {GENRES.map((genre) => (
          <Link
            key={genre.id}
            to="/genres/$genreId"
            params={{ genreId: genre.id }}
            className="block group"
          >
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-xl transition-all">
              <div className={`bg-gradient-to-br ${genre.color} p-6 text-white`}>
                <div className="text-4xl mb-2">{genre.icon}</div>
                <h3 className="text-2xl font-bold">{genre.name}</h3>
              </div>
              <div className="p-6">
                <p className="text-gray-600 text-sm">{genre.description}</p>
                <div className="mt-4 text-blue-600 font-medium group-hover:underline">
                  Explore →
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
