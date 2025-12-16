/**
 * Genre Configuration
 * This is static configuration data, not mock data.
 * TODO: Move to API endpoint when backend provides /api/v1/genres endpoint
 */

export interface Genre {
  id: string;
  name: string;
  description?: string;
  color?: string;
  icon: string;
}

export const GENRES: readonly Genre[] = [
  {
    id: 'gospel',
    name: 'Gospel',
    description: 'Kirk Franklin-style contemporary gospel with rich harmonies',
    color: 'from-purple-500 to-pink-500',
    icon: '🙏',
  },
  {
    id: 'jazz',
    name: 'Jazz',
    description: 'Bebop, modal, and contemporary jazz piano techniques',
    color: 'from-blue-500 to-cyan-500',
    icon: '🎷',
  },
  {
    id: 'blues',
    name: 'Blues',
    description: 'Chicago, Delta, and jump blues styles',
    color: 'from-indigo-500 to-purple-500',
    icon: '🎸',
  },
  {
    id: 'neosoul',
    name: 'Neo-Soul',
    description: "D'Angelo and Erykah Badu-inspired chord voicings",
    color: 'from-pink-500 to-rose-500',
    icon: '✨',
  },
  {
    id: 'classical',
    name: 'Classical',
    description: 'Baroque, Classical, Romantic, and Impressionist periods',
    color: 'from-amber-500 to-orange-500',
    icon: '🎹',
  },
  {
    id: 'reggae',
    name: 'Reggae',
    description: 'Roots, dancehall, and lovers rock piano styles',
    color: 'from-green-500 to-emerald-500',
    icon: '🌴',
  },
  {
    id: 'latin',
    name: 'Latin',
    description: 'Salsa, bossa nova, samba, and cha-cha rhythms',
    color: 'from-red-500 to-orange-500',
    icon: '🎺',
  },
  {
    id: 'rnb',
    name: 'R&B',
    description: 'Classic, neo, and contemporary R&B progressions',
    color: 'from-violet-500 to-fuchsia-500',
    icon: '🎤',
  },
] as const;

/**
 * Get genre by ID
 */
export function getGenreById(id: string): Genre | undefined {
  return GENRES.find((genre) => genre.id === id);
}

/**
 * Get all genre IDs
 */
export function getGenreIds(): string[] {
  return GENRES.map((genre) => genre.id);
}
