import { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { apiClient } from '../api/client'
import AppLayout from '../components/AppLayout'

interface Project {
  id: string
  name: string
  created_at: string
  updated_at: string
}

export default function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newProjectName, setNewProjectName] = useState('')
  const [creating, setCreating] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editName, setEditName] = useState('')
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null)

  const fetchProjects = useCallback(async () => {
    try {
      const response = await apiClient('/api/projects')
      if (!response.ok) throw new Error('Failed to fetch projects')
      const data = await response.json()
      setProjects(data)
    } catch {
      setError('Failed to load projects')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchProjects()
  }, [fetchProjects])

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!newProjectName.trim()) return
    setCreating(true)
    try {
      const response = await apiClient('/api/projects', {
        method: 'POST',
        body: { name: newProjectName.trim() },
      })
      if (!response.ok) throw new Error('Failed to create project')
      setNewProjectName('')
      setShowCreateForm(false)
      await fetchProjects()
    } catch {
      setError('Failed to create project')
    } finally {
      setCreating(false)
    }
  }

  async function handleRename(id: string) {
    if (!editName.trim()) return
    try {
      const response = await apiClient(`/api/projects/${id}`, {
        method: 'PUT',
        body: { name: editName.trim() },
      })
      if (!response.ok) throw new Error('Failed to rename project')
      setEditingId(null)
      setEditName('')
      await fetchProjects()
    } catch {
      setError('Failed to rename project')
    }
  }

  async function handleDelete(id: string) {
    try {
      const response = await apiClient(`/api/projects/${id}`, {
        method: 'DELETE',
      })
      if (!response.ok) throw new Error('Failed to delete project')
      setDeleteConfirmId(null)
      await fetchProjects()
    } catch {
      setError('Failed to delete project')
    }
  }

  function startEditing(project: Project) {
    setEditingId(project.id)
    setEditName(project.name)
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
        <p className="text-gray-500">Loading projects...</p>
      </div>
    )
  }

  return (
    <AppLayout title="My Projects">
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

      <div className="mb-6">
        {showCreateForm ? (
          <form
            onSubmit={handleCreate}
            className="flex flex-col gap-2 sm:flex-row"
          >
            <input
              type="text"
              value={newProjectName}
              onChange={(e) => setNewProjectName(e.target.value)}
              placeholder="Project name"
              autoFocus
              className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <div className="flex gap-2">
              <button
                type="submit"
                disabled={creating || !newProjectName.trim()}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {creating ? 'Creating...' : 'Create'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowCreateForm(false)
                  setNewProjectName('')
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
            New Project
          </button>
        )}
      </div>

      {projects.length === 0 ? (
        <div className="rounded-lg border-2 border-dashed border-gray-300 p-8 text-center sm:p-12">
          <p className="text-gray-500">No projects yet.</p>
          <p className="mt-1 text-sm text-gray-400">
            Create your first project to get started.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {projects.map((project) => (
            <div
              key={project.id}
              className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
            >
              {deleteConfirmId === project.id ? (
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <p className="text-sm text-gray-700">
                    Delete &quot;{project.name}&quot;? This cannot be undone.
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleDelete(project.id)}
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
              ) : editingId === project.id ? (
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                  <input
                    type="text"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') handleRename(project.id)
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
                      onClick={() => handleRename(project.id)}
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
                    to={`/projects/${project.id}`}
                    className="min-w-0 flex-1 hover:text-blue-600"
                  >
                    <h2 className="truncate text-lg font-medium text-gray-900">
                      {project.name}
                    </h2>
                    <p className="text-sm text-gray-500">
                      Updated {formatDate(project.updated_at)}
                    </p>
                  </Link>
                  <div className="flex shrink-0 gap-1 sm:gap-2">
                    <button
                      onClick={() => startEditing(project)}
                      className="rounded-md px-2 py-1.5 text-sm text-gray-500 hover:bg-gray-100 hover:text-gray-700 sm:px-3"
                    >
                      Rename
                    </button>
                    <button
                      onClick={() => setDeleteConfirmId(project.id)}
                      className="rounded-md px-2 py-1.5 text-sm text-red-500 hover:bg-red-50 hover:text-red-700 sm:px-3"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </AppLayout>
  )
}
