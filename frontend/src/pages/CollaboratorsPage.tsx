import { useEffect, useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { apiClient } from '../api/client'
import AppLayout from '../components/AppLayout'

interface Collaborator {
  id: string
  project_id: string
  invitee_id: string
  invitee_email: string
  role: 'viewer' | 'editor' | 'admin'
  status: 'pending' | 'accepted' | 'declined'
  created_at: string
  updated_at: string
}

interface Project {
  id: string
  name: string
  my_role: string | null
}

const ROLES = ['viewer', 'editor', 'admin'] as const
type Role = (typeof ROLES)[number]

const STATUS_STYLES: Record<string, string> = {
  accepted: 'bg-green-100 text-green-700',
  pending: 'bg-yellow-100 text-yellow-700',
  declined: 'bg-gray-100 text-gray-500',
}

const ROLE_STYLES: Record<string, string> = {
  viewer: 'bg-gray-100 text-gray-600',
  editor: 'bg-green-100 text-green-700',
  admin: 'bg-purple-100 text-purple-700',
}

export default function CollaboratorsPage() {
  const { id } = useParams<{ id: string }>()
  const [project, setProject] = useState<Project | null>(null)
  const [collaborators, setCollaborators] = useState<Collaborator[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState<Role>('viewer')
  const [inviting, setInviting] = useState(false)
  const [inviteError, setInviteError] = useState('')
  const [confirmRemoveId, setConfirmRemoveId] = useState<string | null>(null)
  const [removing, setRemoving] = useState(false)

  const fetchProject = useCallback(async () => {
    const response = await apiClient(`/api/projects/${id}`)
    if (!response.ok) throw new Error('Failed to fetch project')
    const data = await response.json()
    setProject(data)
  }, [id])

  const fetchCollaborators = useCallback(async () => {
    const response = await apiClient(`/api/projects/${id}/collaborators`)
    if (!response.ok) throw new Error('Failed to fetch collaborators')
    const data = await response.json()
    setCollaborators(data)
  }, [id])

  useEffect(() => {
    async function load() {
      try {
        await Promise.all([fetchProject(), fetchCollaborators()])
      } catch {
        setError('Failed to load collaborators')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [fetchProject, fetchCollaborators])

  async function handleInvite(e: React.FormEvent) {
    e.preventDefault()
    if (!inviteEmail.trim()) return
    setInviting(true)
    setInviteError('')
    try {
      const response = await apiClient(`/api/projects/${id}/collaborators`, {
        method: 'POST',
        body: { identifier: inviteEmail.trim(), role: inviteRole },
      })
      if (response.status === 404) {
        setInviteError('No user found with that email.')
        return
      }
      if (response.status === 409) {
        setInviteError('That user already has a pending or accepted invitation.')
        return
      }
      if (!response.ok) {
        setInviteError('Failed to send invitation.')
        return
      }
      setInviteEmail('')
      setInviteRole('viewer')
      await fetchCollaborators()
    } catch {
      setInviteError('Failed to send invitation.')
    } finally {
      setInviting(false)
    }
  }

  async function handleRemove(collaboratorId: string) {
    setRemoving(true)
    try {
      const response = await apiClient(`/api/projects/${id}/collaborators/${collaboratorId}`, {
        method: 'DELETE',
      })
      if (!response.ok) {
        setError('Failed to remove collaborator.')
        return
      }
      setCollaborators((prev) => prev.filter((c) => c.id !== collaboratorId))
    } catch {
      setError('Failed to remove collaborator.')
    } finally {
      setRemoving(false)
      setConfirmRemoveId(null)
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-500">Loading collaborators...</p>
      </div>
    )
  }

  const isOwner = project?.my_role === 'owner'
  const isAdmin = project?.my_role === 'admin'
  const canManage = isOwner || isAdmin

  return (
    <AppLayout
      title="Collaborators"
      breadcrumbs={[
        { label: 'Dashboard', to: '/dashboard' },
        { label: project?.name || 'Project', to: `/projects/${id}` },
        { label: 'Collaborators' },
      ]}
    >
      {error && (
        <div className="mb-4 rounded-md bg-red-50 p-3 text-sm text-red-700">
          {error}
          <button onClick={() => setError('')} className="ml-2 font-medium underline">
            Dismiss
          </button>
        </div>
      )}

      {canManage && (
        <div className="mb-6 rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <h2 className="mb-3 text-sm font-semibold text-gray-700">Invite a collaborator</h2>
          <form onSubmit={handleInvite} className="flex flex-col gap-2 sm:flex-row sm:items-end">
            <div className="flex-1">
              <label className="mb-1 block text-xs text-gray-500">Email</label>
              <input
                type="email"
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                placeholder="user@example.com"
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs text-gray-500">Role</label>
              <select
                value={inviteRole}
                onChange={(e) => setInviteRole(e.target.value as Role)}
                className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                {ROLES.map((r) => (
                  <option key={r} value={r}>
                    {r.charAt(0).toUpperCase() + r.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <button
              type="submit"
              disabled={inviting || !inviteEmail.trim()}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {inviting ? 'Inviting...' : 'Invite'}
            </button>
          </form>
          {inviteError && <p className="mt-2 text-sm text-red-600">{inviteError}</p>}
        </div>
      )}

      {collaborators.length === 0 ? (
        <div className="rounded-lg border-2 border-dashed border-gray-300 p-8 text-center">
          <p className="text-gray-500">No collaborators yet.</p>
          <p className="mt-1 text-sm text-gray-400">
            Invite someone above to start collaborating.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {collaborators.map((collab) => {
            const isAccepted = collab.status === 'accepted'
            const rowClass = isAccepted
              ? 'rounded-lg border border-gray-200 bg-white p-4 shadow-sm'
              : 'rounded-lg border border-gray-200 bg-gray-50 p-4 shadow-sm opacity-75'
            return (
              <div key={collab.id} className={rowClass}>
                <div className="flex items-center justify-between gap-2">
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-gray-900">
                      {collab.invitee_email}
                    </p>
                  </div>
                  <div className="flex shrink-0 items-center gap-2">
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-semibold capitalize ${ROLE_STYLES[collab.role] ?? 'bg-gray-100 text-gray-600'}`}
                    >
                      {collab.role}
                    </span>
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-semibold capitalize ${STATUS_STYLES[collab.status] ?? 'bg-gray-100 text-gray-500'}`}
                    >
                      {collab.status}
                    </span>
                    {isOwner && (
                      <button
                        onClick={() => setConfirmRemoveId(collab.id)}
                        className="rounded px-2 py-1 text-xs font-medium text-red-600 hover:bg-red-50"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      <div className="mt-6">
        <Link
          to={`/projects/${id}`}
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          ← Back to project
        </Link>
      </div>

      {confirmRemoveId && (() => {
        const target = collaborators.find((c) => c.id === confirmRemoveId)
        return (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
            <div className="w-full max-w-sm rounded-lg bg-white p-6 shadow-xl">
              <h2 className="mb-2 text-base font-semibold text-gray-900">Remove collaborator</h2>
              <p className="mb-4 text-sm text-gray-600">
                Remove <span className="font-medium">{target?.invitee_email}</span> from this
                project?
              </p>
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => setConfirmRemoveId(null)}
                  disabled={removing}
                  className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleRemove(confirmRemoveId)}
                  disabled={removing}
                  className="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
                >
                  {removing ? 'Removing...' : 'Remove'}
                </button>
              </div>
            </div>
          </div>
        )
      })()}
    </AppLayout>
  )
}
