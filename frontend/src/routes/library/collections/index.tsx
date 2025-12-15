import { createFileRoute, Link } from '@tanstack/react-router';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Music, LayoutGrid, Clock, Lock, Globe } from 'lucide-react';
import { useState } from 'react';
import { collectionsApi, type Collection } from '../../../lib/api';

export const Route = createFileRoute('/library/collections/')({
    component: CollectionsPage,
});

function CollectionsPage() {
    const queryClient = useQueryClient();
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

    // Fetch collections
    const { data: collections, isLoading } = useQuery({
        queryKey: ['collections'],
        queryFn: collectionsApi.list,
    });

    return (
        <div className="flex-1 flex flex-col bg-slate-900 overflow-hidden">
            <header className="flex-shrink-0 p-6 bg-gradient-to-b from-slate-800/80 to-transparent">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-white mb-1">Collections</h1>
                        <p className="text-slate-400">Organize your songs into playlists and setlists</p>
                    </div>
                    <button
                        onClick={() => setIsCreateModalOpen(true)}
                        className="btn-primary flex items-center gap-2"
                    >
                        <Plus className="w-5 h-5" />
                        New Collection
                    </button>
                </div>
            </header>

            <main className="flex-1 overflow-y-auto p-6">
                {isLoading ? (
                    <div className="flex justify-center p-12">
                        <div className="animate-spin w-8 h-8 border-4 border-cyan-500/30 border-t-cyan-500 rounded-full" />
                    </div>
                ) : collections?.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-64 text-center">
                        <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mb-4">
                            <LayoutGrid className="w-8 h-8 text-slate-500" />
                        </div>
                        <h3 className="text-xl font-semibold text-white mb-2">No collections yet</h3>
                        <p className="text-slate-400 max-w-sm mb-6">
                            Create collections to organize your practice material, setlists, or favorites.
                        </p>
                        <button
                            onClick={() => setIsCreateModalOpen(true)}
                            className="text-cyan-400 hover:text-cyan-300 font-medium"
                        >
                            Create your first collection
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {collections?.map((collection) => (
                            <CollectionCard key={collection.id} collection={collection} />
                        ))}
                    </div>
                )}
            </main>

            <CreateCollectionModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
            />
        </div>
    );
}

function CollectionCard({ collection }: { collection: Collection }) {
    return (
        <Link
            to="/library/collections/$collectionId"
            params={{ collectionId: collection.id }}
            className="card p-6 group hover:border-cyan-500/30 transition-all hover:-translate-y-1 block"
        >
            <div className="flex items-start justify-between mb-4">
                <div className="w-12 h-12 bg-slate-800 rounded-xl flex items-center justify-center text-cyan-400 group-hover:scale-110 transition-transform">
                    <Music className="w-6 h-6" />
                </div>
                {collection.is_public ? (
                    <Globe className="w-4 h-4 text-slate-500" />
                ) : (
                    <Lock className="w-4 h-4 text-slate-500" />
                )}
            </div>

            <h3 className="text-lg font-semibold text-white mb-1 group-hover:text-cyan-400 transition-colors">
                {collection.title}
            </h3>
            <p className="text-sm text-slate-400 mb-4 line-clamp-2 min-h-[2.5em]">
                {collection.description || <span className="italic text-slate-600">No description</span>}
            </p>

            <div className="flex items-center justify-between text-xs text-slate-500 pt-4 border-t border-slate-700/50">
                <span>{collection.item_count} songs</span>
                <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(collection.updated_at).toLocaleDateString()}
                </span>
            </div>
        </Link>
    );
}

function CreateCollectionModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
    const queryClient = useQueryClient();
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [isPublic, setIsPublic] = useState(false);

    const createMutation = useMutation({
        mutationFn: collectionsApi.create,
        onSuccess: (newCollection) => {
            queryClient.setQueryData(['collections'], (old: Collection[] | undefined) => {
                return old ? [newCollection, ...old] : [newCollection];
            });
            onClose();
            setTitle('');
            setDescription('');
        },
    });

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-slate-900 rounded-xl border border-slate-700 shadow-xl w-full max-w-md p-6">
                <h2 className="text-xl font-bold text-white mb-4">New Collection</h2>
                <form onSubmit={(e) => { e.preventDefault(); createMutation.mutate({ title, description, is_public: isPublic }); }}>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Title</label>
                            <input
                                type="text"
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                                className="input-field"
                                placeholder="My Favorites"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">Description</label>
                            <textarea
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                className="input-field min-h-[80px]"
                                placeholder="Optional description..."
                            />
                        </div>
                        <div className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                id="public"
                                checked={isPublic}
                                onChange={(e) => setIsPublic(e.target.checked)}
                                className="rounded bg-slate-800 border-slate-700 text-cyan-500"
                            />
                            <label htmlFor="public" className="text-sm text-slate-300">Public collection</label>
                        </div>
                    </div>
                    <div className="flex justify-end gap-2 mt-6">
                        <button type="button" onClick={onClose} className="btn-secondary">Cancel</button>
                        <button type="submit" className="btn-primary" disabled={createMutation.isPending}>
                            {createMutation.isPending ? 'Creating...' : 'Create Collection'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
