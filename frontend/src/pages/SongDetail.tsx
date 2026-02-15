import { useEffect, useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { apiClient } from '../api/client'
import { useAuth } from '../auth/useAuth'
import GuitarNeck, { type Marker } from '../components/GuitarNeck'

interface Song {
  id: string
  name: string
  project_id: string
}

interface Project {
  id: string
  name: string
}

interface Chord {
  id: string
  name: string | null
  markers: Marker[]
  string_count: number
  tuning: string
  position: number
}

export default function SongDetail() {
  const { id } = useParams<{ id: string }>()
  const { logout } = useAuth()
  const [song, setSong] = useState<Song | null>(null)
  const [project, setProject] = useState<Project | null>(null)
  const [chords, setChords] = useState<Chord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchSong = useCallback(async () => {
    const response = await apiClient(`/api/songs/${id}`)
    if (!response.ok) throw new Error('Failed to fetch song')
    const data = await response.json()
    setSong(data)
    return data as Song
  }, [id])

  const fetchChords = useCallback(async () => {
    const response = await apiClient(`/api/songs/${id}/chords`)
    if (!response.ok) throw new Error('Failed to fetch chords')
    const data = await response.json()
    setChords(data)
  }, [id])

  useEffect(() => {
    async function load() {
      try {
        const songData = await fetchSong()
        const projectResponse = await apiClient(
          `/api/projects/${songData.project_id}`,
        )
        if (projectResponse.ok) {
          const projectData = await projectResponse.json()
          setProject(projectData)
        }
        await fetchChords()
      } catch {
        setError('Failed to load song')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [fetchSong, fetchChords])

  async function handleAddChord() {
    try {
      const response = await apiClient(`/api/songs/${id}/chords`, {
        method: 'POST',
        body: { markers: [] },
      })
      if (!response.ok) throw new Error('Failed to create chord')
      await fetchChords()
    } catch {
      setError('Failed to add chord')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">Loading chords...</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="mx-auto max-w-4xl px-4 py-4 flex items-center justify-between">
          <div>
            <nav className="text-sm text-gray-500 mb-1">
              <Link to="/dashboard" className="hover:text-blue-600">
                Dashboard
              </Link>
              <span className="mx-1">/</span>
              {project && (
                <>
                  <Link
                    to={`/projects/${project.id}`}
                    className="hover:text-blue-600"
                  >
                    {project.name}
                  </Link>
                  <span className="mx-1">/</span>
                </>
              )}
              <span className="text-gray-900">{song?.name}</span>
            </nav>
            <h1 className="text-2xl font-bold text-gray-900">{song?.name}</h1>
          </div>
          <button
            onClick={logout}
            className="text-sm text-gray-500 hover:text-gray-700"
          >
            Log out
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-4xl px-4 py-8">
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

        {chords.length === 0 ? (
          <div className="rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
            <p className="text-gray-500">No chords yet.</p>
            <p className="mt-1 text-sm text-gray-400">
              Add your first chord to start building your progression.
            </p>
            <button
              onClick={handleAddChord}
              className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              Add Chord
            </button>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
              {chords.map((chord) => (
                <div
                  key={chord.id}
                  className="rounded-lg border border-gray-200 bg-white p-3 shadow-sm"
                >
                  <p className="mb-2 text-sm font-medium text-gray-900 truncate">
                    {chord.name || 'Untitled'}
                  </p>
                  <div className="pointer-events-none">
                    <GuitarNeck
                      markers={chord.markers}
                      stringCount={chord.string_count || 6}
                      tuning={chord.tuning || 'EADGBE'}
                      fretCount={5}
                    />
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-6">
              <button
                onClick={handleAddChord}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
              >
                Add Chord
              </button>
            </div>
          </>
        )}
      </main>
    </div>
  )
}
