import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Plus, Loader2, Music, Lock, Globe } from 'lucide-react';
import { collectionsApi, type Collection } from '../../lib/api';

interface AddToCollectionModalProps {
    isOpen: boolean;
    onClose: () => void;
    songId: string;
}

export function AddToCollectionModal({ isOpen, onClose, songId }: AddToCollectionModalProps) {
    const queryClient = useQueryClient();
    const [createMode, setCreateMode] = useState(false);
    const [newTitle, setNewTitle] = useState('');
    const [isPublic, setIsPublic] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');

    // Fetch collections
    const { data: collections, isLoading } = useQuery({
        queryKey: ['collections'],
        queryFn: collectionsApi.list,
        enabled: isOpen,
    });

    // Create collection mutation
    const createMutation = useMutation({
        mutationFn: collectionsApi.create,
        onSuccess: (newCollection) => {
            queryClient.setQueryData(['collections'], (old: Collection[] | undefined) => {
                return old ? [newCollection, ...old] : [newCollection];
            });
            setCreateMode(false);
            setNewTitle('');
            // Automatically add to the new collection?
            addMutation.mutate({ collectionId: newCollection.id, songId });
        },
    });

    // Add to collection mutation
    const addMutation = useMutation({
        mutationFn: ({ collectionId, songId }: { collectionId: string, songId: string }) =>
            collectionsApi.addItem(collectionId, songId),
        onSuccess: () => {
            onClose();
        },
    });

    const filteredCollections = collections?.filter(c =>
        c.title.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleCreate = (e: React.FormEvent) => {
        e.preventDefault();
        if (!newTitle.trim()) return;
        createMutation.mutate({ title: newTitle, is_public: isPublic });
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
                    />
                    <div className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none p-4">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: 20 }}
                            className="bg-slate-900 rounded-xl border border-slate-700 shadow-xl w-full max-w-md pointer-events-auto overflow-hidden"
                            onClick={(e) => e.stopPropagation()}
                        >
                            {/* Header */}
                            <div className="flex items-center justify-between p-4 border-b border-slate-700/50 bg-slate-800/30">
                                <h3 className="font-semibold text-white">Add to Collection</h3>
                                <button
                                    onClick={onClose}
                                    className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700/50 transition-colors"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </div>

                            {/* Content */}
                            <div className="p-4">
                                {createMode ? (
                                    <form onSubmit={handleCreate} className="space-y-4">
                                        <div>
                                            <input
                                                type="text"
                                                placeholder="Collection Title"
                                                value={newTitle}
                                                onChange={(e) => setNewTitle(e.target.value)}
                                                className="w-full bg-slate-800 border-none rounded-lg px-4 py-2 text-white placeholder-slate-500 focus:ring-1 focus:ring-cyan-500"
                                                autoFocus
                                            />
                                        </div>
                                        <div className="flex items-center gap-2 text-sm text-slate-400">
                                            <button
                                                type="button"
                                                onClick={() => setIsPublic(!isPublic)}
                                                className={`flex items-center gap-2 px-3 py-1.5 rounded-full border transition-colors ${isPublic
                                                    ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400'
                                                    : 'bg-slate-800 border-slate-700 text-slate-400'
                                                    }`}
                                            >
                                                {isPublic ? <Globe className="w-4 h-4" /> : <Lock className="w-4 h-4" />}
                                                {isPublic ? 'Public' : 'Private'}
                                            </button>
                                        </div>
                                        <div className="flex justify-end gap-2">
                                            <button
                                                type="button"
                                                onClick={() => setCreateMode(false)}
                                                className="px-3 py-1.5 text-slate-400 hover:text-white"
                                            >
                                                Cancel
                                            </button>
                                            <button
                                                type="submit"
                                                disabled={!newTitle.trim() || createMutation.isPending}
                                                className="px-3 py-1.5 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg disabled:opacity-50 flex items-center gap-2"
                                            >
                                                {createMutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
                                                Create
                                            </button>
                                        </div>
                                    </form>
                                ) : (
                                    <div className="space-y-3">
                                        <div className="flex gap-2">
                                            <input
                                                type="text"
                                                placeholder="Search collections..."
                                                value={searchTerm}
                                                onChange={(e) => setSearchTerm(e.target.value)}
                                                className="flex-1 bg-slate-800 border-none rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:ring-1 focus:ring-cyan-500"
                                            />
                                            <button
                                                onClick={() => setCreateMode(true)}
                                                className="p-2 bg-slate-800 hover:bg-slate-700 text-cyan-400 rounded-lg transition-colors tooltip"
                                                title="New Collection"
                                            >
                                                <Plus className="w-5 h-5" />
                                            </button>
                                        </div>

                                        <div className="max-h-60 overflow-y-auto space-y-1 pr-1">
                                            {isLoading ? (
                                                <div className="flex justify-center p-4">
                                                    <Loader2 className="w-6 h-6 animate-spin text-slate-500" />
                                                </div>
                                            ) : filteredCollections?.length === 0 ? (
                                                <p className="text-center text-slate-500 py-4 text-sm">
                                                    No collections found. Create one!
                                                </p>
                                            ) : (
                                                filteredCollections?.map(collection => (
                                                    <button
                                                        key={collection.id}
                                                        onClick={() => addMutation.mutate({ collectionId: collection.id, songId })}
                                                        disabled={addMutation.isPending}
                                                        className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-slate-800/50 group transition-colors text-left"
                                                    >
                                                        <div className="flex items-center gap-3 overflow-hidden">
                                                            <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center text-slate-500 flex-shrink-0">
                                                                <Music className="w-5 h-5" />
                                                            </div>
                                                            <div className="min-w-0">
                                                                <h4 className="font-medium text-slate-200 truncate group-hover:text-cyan-400 transition-colors">
                                                                    {collection.title}
                                                                </h4>
                                                                <p className="text-xs text-slate-500">
                                                                    {collection.item_count} items • {collection.is_public ? 'Public' : 'Private'}
                                                                </p>
                                                            </div>
                                                        </div>
                                                        {addMutation.variables?.collectionId === collection.id && addMutation.isPending ? (
                                                            <Loader2 className="w-5 h-5 animate-spin text-slate-500" />
                                                        ) : (
                                                            <Plus className="w-5 h-5 text-slate-600 group-hover:text-cyan-400 opacity-0 group-hover:opacity-100 transition-all" />
                                                        )}
                                                    </button>
                                                ))
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </motion.div>
                    </div>
                </>
            )}
        </AnimatePresence>
    );
}
