import { useEffect, useState } from 'react'
import { apiClient } from '../api/client'

interface PendingInvitation {
  id: string
  project_id: string
  project_name: string
  inviter_email: string
  role: 'viewer' | 'editor' | 'admin'
  status: string
  created_at: string
  updated_at: string
}

interface Props {
  onClose: () => void
  onAccept?: () => void
}

export default function PendingInvitationsModal({ onClose, onAccept }: Props) {
  const [invitations, setInvitations] = useState<PendingInvitation[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchPending() {
      try {
        const response = await apiClient('/api/collaborators/pending')
        if (response.ok) {
          const data = await response.json()
          setInvitations(data)
        }
      } finally {
        setLoading(false)
      }
    }
    fetchPending()
  }, [])

  function removeInvitation(id: string) {
    setInvitations((prev) => prev.filter((inv) => inv.id !== id))
  }

  async function handleAccept(invitation: PendingInvitation) {
    const response = await apiClient(`/api/collaborators/${invitation.id}`, {
      method: 'PATCH',
      body: { status: 'accepted' },
    })
    if (response.ok) {
      removeInvitation(invitation.id)
      onAccept?.()
    }
  }

  async function handleDecline(invitation: PendingInvitation) {
    const response = await apiClient(`/api/collaborators/${invitation.id}`, {
      method: 'PATCH',
      body: { status: 'declined' },
    })
    if (response.ok) {
      removeInvitation(invitation.id)
    }
  }

  if (loading || invitations.length === 0) return null

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/40 px-4 pt-16">
      <div className="w-full max-w-md rounded-xl bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-gray-200 px-5 py-4">
          <h2 className="text-base font-semibold text-gray-900">
            Pending Invitations ({invitations.length})
          </h2>
          <button
            onClick={onClose}
            className="rounded-md p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
            aria-label="Dismiss"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        </div>

        <ul className="divide-y divide-gray-100">
          {invitations.map((inv) => (
            <li key={inv.id} className="px-5 py-4">
              <p className="font-medium text-gray-900">{inv.project_name}</p>
              <p className="mt-0.5 text-sm text-gray-500">
                Invited by {inv.inviter_email} &middot; Role:{' '}
                <span className="capitalize">{inv.role}</span>
              </p>
              <div className="mt-3 flex gap-2">
                <button
                  onClick={() => handleAccept(inv)}
                  className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
                >
                  Accept
                </button>
                <button
                  onClick={() => handleDecline(inv)}
                  className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Decline
                </button>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
