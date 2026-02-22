import { useEffect, useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { apiClient } from '../api/client'
import AppLayout from '../components/AppLayout'


interface Project {
  id: string
  name: string
  my_role: string | null
}

interface Song {
  id: string
  name: string
  created_at: string
  updated_at: string
}

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>()
  const [project, setProject] = useState<Project | null>(null)
  const [songs, setSongs] = useState<Song[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newSongName, setNewSongName] = useState('')
  const [creating, setCreating] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editName, setEditName] = useState('')
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null)

  const fetchProject = useCallback(async () => {
    try {
      const response = await apiClient(`/api/projects/${id}`)
      if (!response.ok) throw new Error('Failed to fetch project')
      const data = await response.json()
      setProject(data)
    } catch {
      setError('Failed to load project')
    }
  }, [id])

  const fetchSongs = useCallback(async () => {
    try {
      const response = await apiClient(`/api/projects/${id}/songs`)
      if (!response.ok) throw new Error('Failed to fetch songs')
      const data = await response.json()
      setSongs(data)
    } catch {
      setError('Failed to load songs')
    }
  }, [id])

  useEffect(() => {
    async function load() {
      await Promise.all([fetchProject(), fetchSongs()])
      setLoading(false)
    }
    load()
  }, [fetchProject, fetchSongs])

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!newSongName.trim()) return
    setCreating(true)
    try {
      const response = await apiClient(`/api/projects/${id}/songs`, {
        method: 'POST',
        body: { name: newSongName.trim() },
      })
      if (!response.ok) throw new Error('Failed to create song')
      setNewSongName('')
      setShowCreateForm(false)
      await fetchSongs()
    } catch {
      setError('Failed to create song')
    } finally {
      setCreating(false)
    }
  }

  async function handleRename(songId: string) {
    if (!editName.trim()) return
    try {
      const response = await apiClient(`/api/songs/${songId}`, {
        method: 'PUT',
        body: { name: editName.trim() },
      })
      if (!response.ok) throw new Error('Failed to rename song')
      setEditingId(null)
      setEditName('')
      await fetchSongs()
    } catch {
      setError('Failed to rename song')
    }
  }

  async function handleDelete(songId: string) {
    try {
      const response = await apiClient(`/api/songs/${songId}`, {
        method: 'DELETE',
      })
      if (!response.ok) throw new Error('Failed to delete song')
      setDeleteConfirmId(null)
      await fetchSongs()
    } catch {
      setError('Failed to delete song')
    }
  }

  function startEditing(song: Song) {
    setEditingId(song.id)
    setEditName(song.name)
  }

  function formatDate(dateString: string) {
    return new Date(dateString).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-500">Loading songs...</p>
      </div>
    )
  }

  const canEdit = ['owner', 'admin', 'editor'].includes(project?.my_role ?? '')
  const canManage = ['owner', 'admin'].includes(project?.my_role ?? '')

  const roleBadgeColors: Record<string, string> = {
    owner: 'bg-blue-100 text-blue-700',
    admin: 'bg-purple-100 text-purple-700',
    editor: 'bg-green-100 text-green-700',
    viewer: 'bg-gray-100 text-gray-600',
  }

  return (
    <AppLayout
      title={project?.name || 'Project'}
      breadcrumbs={[
        { label: 'Dashboard', to: '/dashboard' },
        { label: project?.name || 'Project' },
      ]}
    >
      {error && (
        <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-700">
          {error}
          <button
            onClick={() => setError('')}
            className="ml-2 font-medium underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {project?.my_role && (
        <div className="mb-4 flex items-center justify-between gap-2">
          <span
            className={`rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ${roleBadgeColors[project.my_role] ?? 'bg-gray-100 text-gray-600'}`}
          >
            {project.my_role}
          </span>
          {canManage && (
            <Link
              to={`/projects/${id}/collaborators`}
              className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Collaborators
            </Link>
          )}
        </div>
      )}

      <div className="mb-6">
        {canEdit && (showCreateForm ? (
          <form
            onSubmit={handleCreate}
            className="flex flex-col gap-2 sm:flex-row"
          >
            <input
              type="text"
              value={newSongName}
              onChange={(e) => setNewSongName(e.target.value)}
              placeholder="Song name"
              autoFocus
              className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={creating || !newSongName.trim()}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {creating ? 'Creating...' : 'Create'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowCreateForm(false)
                  setNewSongName('')
                }}
                className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </form>
        ) : (
          <button
            onClick={() => setShowCreateForm(true)}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            New Song
          </button>
        ))}
      </div>

      {songs.length === 0 ? (
        <div className="rounded-lg border-2 border-dashed border-gray-300 p-8 text-center sm:p-12">
          <p className="text-gray-500">No songs yet.</p>
          <p className="mt-1 text-sm text-gray-400">
            Create your first song to start adding chords.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {songs.map((song) => (
            <div
              key={song.id}
              className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
            >
              {deleteConfirmId === song.id ? (
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <p className="text-sm text-gray-700">
                    Delete &quot;{song.name}&quot;? This cannot be undone.
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleDelete(song.id)}
                      className="rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700"
                    >
                      Delete
                    </button>
                    <button
                      onClick={() => setDeleteConfirmId(null)}
                      className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : editingId === song.id ? (
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                  <input
                    type="text"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleRename(song.id)
                      if (e.key === 'Escape') {
                        setEditingId(null)
                        setEditName('')
                      }
                    }}
                    autoFocus
                    className="flex-1 rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleRename(song.id)}
                      disabled={!editName.trim()}
                      className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                    >
                      Save
                    </button>
                    <button
                      onClick={() => {
                        setEditingId(null)
                        setEditName('')
                      }}
                      className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-between gap-2">
                  <Link
                    to={`/songs/${song.id}`}
                    className="min-w-0 flex-1 hover:text-blue-600"
                  >
                    <h2 className="truncate text-lg font-medium text-gray-900">
                      {song.name}
                    </h2>
                    <p className="text-sm text-gray-500">
                      Updated {formatDate(song.updated_at)}
                    </p>
                  </Link>
                  {canEdit && (
                    <div className="flex shrink-0 gap-1 sm:gap-2">
                      <button
                        onClick={() => startEditing(song)}
                        className="rounded-md px-2 py-1.5 text-sm text-gray-500 hover:bg-gray-100 hover:text-gray-700 sm:px-3"
                      >
                        Rename
                      </button>
                      <button
                        onClick={() => setDeleteConfirmId(song.id)}
                        className="rounded-md px-2 py-1.5 text-sm text-red-500 hover:bg-red-50 hover:text-red-700 sm:px-3"
                      >
                        Delete
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </AppLayout>
  )
}
