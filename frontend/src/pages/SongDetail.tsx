import { useEffect, useState, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core'
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import { apiClient } from '../api/client'
import AppLayout from '../components/AppLayout'
import GuitarNeck, { type Marker } from '../components/GuitarNeck'
import ChordStaff from '../components/ChordStaff'
import {
  buildDefaultMeasures,
  type SequenceApiResponse,
  type SequenceMeasure,
} from '../types/sequence'
import { chordTemplates } from '../data/chordTemplates'

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
  starting_fret: number
}

interface SortableChordCardProps {
  chord: Chord
  index: number
  total: number
  onEdit: (chord: Chord) => void
  onDelete: (chord: Chord) => void
  onMoveUp: (index: number) => void
  onMoveDown: (index: number) => void
}

function SortableChordCard({
  chord,
  index,
  total,
  onEdit,
  onDelete,
  onMoveUp,
  onMoveDown,
}: SortableChordCardProps) {
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: chord.id })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="rounded-lg border border-gray-200 bg-white p-3 shadow-sm"
    >
      <div className="flex items-start gap-2">
        {/* Drag handle */}
        <button
          type="button"
          className="mt-1 cursor-grab touch-none text-gray-400 hover:text-gray-600"
          aria-label="Drag to reorder"
          {...attributes}
          {...listeners}
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="currentColor"
          >
            <circle cx="5" cy="3" r="1.5" />
            <circle cx="11" cy="3" r="1.5" />
            <circle cx="5" cy="8" r="1.5" />
            <circle cx="11" cy="8" r="1.5" />
            <circle cx="5" cy="13" r="1.5" />
            <circle cx="11" cy="13" r="1.5" />
          </svg>
        </button>

        <div className="min-w-0 flex-1">
          {/* Chord name + actions row */}
          <div className="mb-2 flex items-center justify-between">
            <button
              type="button"
              onClick={() => onEdit(chord)}
              className="truncate text-sm font-medium text-gray-900 hover:text-blue-600"
            >
              {chord.name || 'Untitled'}
            </button>
            <div className="ml-2 flex items-center gap-1">
              {/* Move up */}
              <button
                type="button"
                onClick={() => onMoveUp(index)}
                disabled={index === 0}
                className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 disabled:opacity-30 disabled:hover:bg-transparent"
                aria-label="Move up"
              >
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 14 14"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M7 11V3M7 3L3 7M7 3l4 4" />
                </svg>
              </button>
              {/* Move down */}
              <button
                type="button"
                onClick={() => onMoveDown(index)}
                disabled={index === total - 1}
                className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600 disabled:opacity-30 disabled:hover:bg-transparent"
                aria-label="Move down"
              >
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 14 14"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                >
                  <path d="M7 3v8M7 11l-4-4M7 11l4-4" />
                </svg>
              </button>
              {/* Delete */}
              {confirmingDelete ? (
                <span className="flex items-center gap-1 text-xs">
                  <button
                    type="button"
                    onClick={() => onDelete(chord)}
                    className="rounded bg-red-600 px-2 py-0.5 text-white hover:bg-red-700"
                  >
                    Delete
                  </button>
                  <button
                    type="button"
                    onClick={() => setConfirmingDelete(false)}
                    className="rounded border border-gray-300 px-2 py-0.5 text-gray-600 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </span>
              ) : (
                <button
                  type="button"
                  onClick={() => setConfirmingDelete(true)}
                  className="rounded p-1 text-gray-400 hover:bg-red-50 hover:text-red-600"
                  aria-label="Delete chord"
                >
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 14 14"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <path d="M2 4h10M5 4V2h4v2M5 6v5M9 6v5M3 4l1 8h6l1-8" />
                  </svg>
                </button>
              )}
            </div>
          </div>

          {/* Mini guitar neck preview */}
          <button
            type="button"
            onClick={() => onEdit(chord)}
            className="block w-full cursor-pointer"
          >
            <div className="pointer-events-none">
              <GuitarNeck
                markers={chord.markers}
                stringCount={chord.string_count || 6}
                tuning={chord.tuning || 'EADGBE'}
                fretCount={5}
                startingFret={chord.starting_fret ?? 0}
              />
            </div>
          </button>
        </div>
      </div>
    </div>
  )
}

export default function SongDetail() {
  const { id } = useParams<{ id: string }>()
  const [song, setSong] = useState<Song | null>(null)
  const [project, setProject] = useState<Project | null>(null)
  const [chords, setChords] = useState<Chord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Editor state
  const [editorOpen, setEditorOpen] = useState(false)
  const [editingChordId, setEditingChordId] = useState<string | null>(null)
  const [editorMarkers, setEditorMarkers] = useState<Marker[]>([])
  const [editorName, setEditorName] = useState('')
  const [saving, setSaving] = useState(false)
  const [editorStartingFret, setEditorStartingFret] = useState(0)
  const [templateBrowserOpen, setTemplateBrowserOpen] = useState(false)
  const [templateSearch, setTemplateSearch] = useState('')

  // Sequence state (initialized with 4 empty measures in 4/4)
  const [sequenceNumerator, setSequenceNumerator] = useState(4)
  const [sequenceDenominator, setSequenceDenominator] = useState(4)
  const [measuresPerLine, setMeasuresPerLine] = useState(4)
  const [sequenceMeasures, setSequenceMeasures] = useState<SequenceMeasure[]>(
    () => buildDefaultMeasures(4, 4),
  )
  const [sequenceExists, setSequenceExists] = useState(false)
  const [sequenceSaving, setSequenceSaving] = useState(false)
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null)

  function showToast(message: string, type: 'success' | 'error') {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3000)
  }

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  )

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

  const fetchSequence = useCallback(async () => {
    const response = await apiClient(`/api/songs/${id}/sequence`)
    if (response.status === 404) {
      // No sequence yet — keep defaults
      return
    }
    if (!response.ok) throw new Error('Failed to fetch sequence')
    const data: SequenceApiResponse = await response.json()
    setSequenceNumerator(data.time_signature_numerator)
    setSequenceDenominator(data.time_signature_denominator)
    setMeasuresPerLine(data.measures_per_line)
    setSequenceExists(true)
    setSequenceMeasures(
      data.measures
        .sort((a, b) => a.position - b.position)
        .map((m) => ({
          id: m.id,
          position: m.position,
          repeat_start: m.repeat_start,
          repeat_end: m.repeat_end,
          ending_number: m.ending_number,
          beats: m.beats
            .sort((a, b) => a.beat_position - b.beat_position)
            .map((b) => ({
              beat_position: b.beat_position,
              chord_id: b.chord_id,
            })),
        })),
    )
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
        await fetchSequence()
      } catch {
        setError('Failed to load song')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [fetchSong, fetchChords, fetchSequence])

  async function handleSaveSequence() {
    setSequenceSaving(true)
    try {
      const payload = {
        time_signature_numerator: sequenceNumerator,
        time_signature_denominator: sequenceDenominator,
        measures_per_line: measuresPerLine,
        measures: sequenceMeasures.map((m, index) => ({
          position: index,
          repeat_start: m.repeat_start,
          repeat_end: m.repeat_end,
          ending_number: m.ending_number,
          beats: m.beats.map((b) => ({
            beat_position: b.beat_position,
            chord_id: b.chord_id,
          })),
        })),
      }

      let response = await apiClient(`/api/songs/${id}/sequence`, {
        method: 'PUT',
        body: payload,
      })

      if (response.status === 404) {
        // Sequence doesn't exist yet — create it first
        const createResponse = await apiClient(`/api/songs/${id}/sequence`, {
          method: 'POST',
          body: {
            time_signature_numerator: sequenceNumerator,
            time_signature_denominator: sequenceDenominator,
            measures_per_line: measuresPerLine,
          },
        })
        if (!createResponse.ok) throw new Error('Failed to create sequence')
        setSequenceExists(true)
        response = await apiClient(`/api/songs/${id}/sequence`, {
          method: 'PUT',
          body: payload,
        })
      }

      if (!response.ok) throw new Error('Failed to save sequence')
      if (!sequenceExists) setSequenceExists(true)
      showToast('Sequence saved', 'success')
    } catch {
      showToast('Failed to save sequence', 'error')
    } finally {
      setSequenceSaving(false)
    }
  }

  function handleAddMeasure() {
    setSequenceMeasures((prev) => {
      const newMeasure: SequenceMeasure = {
        id: crypto.randomUUID(),
        position: prev.length,
        repeat_start: false,
        repeat_end: false,
        ending_number: null,
        beats: Array.from({ length: sequenceNumerator }, (_, i) => ({
          beat_position: i + 1,
          chord_id: null,
        })),
      }
      return [...prev, newMeasure]
    })
  }

  function handleRemoveMeasure(measureId: string) {
    setSequenceMeasures((prev) =>
      prev
        .filter((m) => m.id !== measureId)
        .map((m, index) => ({ ...m, position: index })),
    )
  }

  function handleRemoveBeat(measureId: string, beatPosition: number) {
    setSequenceMeasures((prev) =>
      prev.map((m) => {
        if (m.id !== measureId) return m
        return {
          ...m,
          beats: m.beats.map((b) =>
            b.beat_position === beatPosition ? { ...b, chord_id: null } : b,
          ),
        }
      }),
    )
  }

  async function persistReorder(reorderedChords: Chord[]) {
    const response = await apiClient(`/api/songs/${id}/chords/reorder`, {
      method: 'PUT',
      body: { chord_ids: reorderedChords.map((c) => c.id) },
    })
    if (!response.ok) {
      setError('Failed to reorder chords')
      await fetchChords()
    }
  }

  async function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event
    if (!over) return

    // Check if dropped on a beat slot
    const beatData = over.data.current as { type?: string; measureId?: string; beatPosition?: number }
    if (beatData?.type === 'beat' && beatData.measureId && beatData.beatPosition !== undefined) {
      const chordId = String(active.id)
      if (chords.some((c) => c.id === chordId)) {
        setSequenceMeasures((prev) =>
          prev.map((m) => {
            if (m.id !== beatData.measureId) return m
            return {
              ...m,
              beats: m.beats.map((b) =>
                b.beat_position === beatData.beatPosition ? { ...b, chord_id: chordId } : b,
              ),
            }
          }),
        )
      }
      return
    }

    // Sortable chord reorder
    if (active.id === over.id) return
    const oldIndex = chords.findIndex((c) => c.id === active.id)
    const newIndex = chords.findIndex((c) => c.id === over.id)
    if (oldIndex === -1 || newIndex === -1) return
    const reordered = arrayMove(chords, oldIndex, newIndex)
    setChords(reordered)
    await persistReorder(reordered)
  }

  async function handleMoveUp(index: number) {
    if (index === 0) return
    const reordered = arrayMove(chords, index, index - 1)
    setChords(reordered)
    await persistReorder(reordered)
  }

  async function handleMoveDown(index: number) {
    if (index === chords.length - 1) return
    const reordered = arrayMove(chords, index, index + 1)
    setChords(reordered)
    await persistReorder(reordered)
  }

  async function handleDeleteChord(chord: Chord) {
    try {
      const response = await apiClient(`/api/chords/${chord.id}`, {
        method: 'DELETE',
      })
      if (!response.ok) throw new Error('Failed to delete chord')
      await fetchChords()
    } catch {
      setError('Failed to delete chord')
    }
  }

  function openNewChordEditor() {
    setEditingChordId(null)
    setEditorMarkers([])
    setEditorName('')
    setEditorStartingFret(0)
    setEditorOpen(true)
  }

  function openEditChordEditor(chord: Chord) {
    setEditingChordId(chord.id)
    setEditorMarkers([...chord.markers])
    setEditorName(chord.name || '')

    const fretCount = 5
    const savedStart = chord.starting_fret ?? 0
    const fretValues = chord.markers.map((m) => m.fret)

    if (fretValues.length === 0) {
      setEditorStartingFret(savedStart)
    } else {
      const maxFret = Math.max(...fretValues)
      const allVisible = fretValues.every(
        (f) =>
          (savedStart === 0 && f === 0) ||
          (f >= savedStart + 1 && f <= savedStart + fretCount),
      )
      if (allVisible) {
        setEditorStartingFret(savedStart)
      } else {
        const minFret = Math.min(...fretValues.filter((f) => f > 0))
        const adjusted = Math.max(0, (Number.isFinite(minFret) ? minFret : 1) - 1)
        // Ensure all markers fit: if max fret exceeds adjusted + fretCount, shift up
        if (maxFret > adjusted + fretCount) {
          setEditorStartingFret(Math.max(0, maxFret - fretCount))
        } else {
          setEditorStartingFret(adjusted)
        }
      }
    }

    setEditorOpen(true)
  }

  function handleMarkerToggle(marker: Marker) {
    setEditorMarkers((prev) => {
      const exists = prev.some(
        (m) => m.string === marker.string && m.fret === marker.fret,
      )
      if (exists) {
        return prev.filter(
          (m) => !(m.string === marker.string && m.fret === marker.fret),
        )
      }
      return [...prev, marker]
    })
  }

  function handleCancel() {
    setEditorOpen(false)
    setEditingChordId(null)
    setEditorMarkers([])
    setEditorName('')
    setEditorStartingFret(0)
    setTemplateBrowserOpen(false)
    setTemplateSearch('')
  }

  async function handleSave() {
    setSaving(true)
    try {
      if (editingChordId) {
        const response = await apiClient(`/api/chords/${editingChordId}`, {
          method: 'PUT',
          body: {
            name: editorName || null,
            markers: editorMarkers,
            starting_fret: editorStartingFret,
          },
        })
        if (!response.ok) throw new Error('Failed to update chord')
      } else {
        const response = await apiClient(`/api/songs/${id}/chords`, {
          method: 'POST',
          body: {
            name: editorName || null,
            markers: editorMarkers,
            starting_fret: editorStartingFret,
          },
        })
        if (!response.ok) throw new Error('Failed to create chord')
      }
      await fetchChords()
      handleCancel()
    } catch {
      setError(
        editingChordId ? 'Failed to update chord' : 'Failed to create chord',
      )
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-500">Loading chords...</p>
      </div>
    )
  }

  const breadcrumbs = [
    { label: 'Dashboard', to: '/dashboard' },
    ...(project
      ? [{ label: project.name, to: `/projects/${project.id}` }]
      : []),
    { label: song?.name || 'Song' },
  ]

  return (
    <AppLayout title={song?.name || 'Song'} breadcrumbs={breadcrumbs}>
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

      {/* Chord Editor Modal */}
      {editorOpen && (
        <div className="fixed inset-0 z-50 flex items-end justify-center sm:items-center">
          <div
            className="fixed inset-0 bg-black/50"
            onClick={handleCancel}
          />
          <div className="relative w-full max-w-lg rounded-t-lg bg-white p-4 shadow-xl sm:mx-4 sm:rounded-lg sm:p-6 max-h-[90vh] overflow-y-auto">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">
              {editingChordId ? 'Edit Chord' : 'New Chord'}
            </h2>
            <div className="mb-4">
              <label
                htmlFor="chord-name"
                className="mb-1 block text-sm font-medium text-gray-700"
              >
                Chord Name (optional)
              </label>
              <input
                id="chord-name"
                type="text"
                value={editorName}
                onChange={(e) => setEditorName(e.target.value)}
                placeholder="e.g. Am, G7, Cadd9"
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div className="mb-3">
              <button
                type="button"
                onClick={() => {
                  setTemplateBrowserOpen(!templateBrowserOpen)
                  setTemplateSearch('')
                }}
                className="text-sm font-medium text-blue-600 hover:text-blue-800"
              >
                {templateBrowserOpen ? 'Hide Templates' : 'Browse Templates'}
              </button>
            </div>
            {templateBrowserOpen && (
              <div className="mb-4 rounded-md border border-gray-200 bg-gray-50 p-3">
                <input
                  type="text"
                  value={templateSearch}
                  onChange={(e) => setTemplateSearch(e.target.value)}
                  placeholder="Search chords..."
                  className="mb-3 w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                <div className="grid grid-cols-3 gap-2 sm:grid-cols-4">
                  {chordTemplates
                    .filter((t) =>
                      t.name
                        .toLowerCase()
                        .includes(templateSearch.toLowerCase()),
                    )
                    .map((template) => (
                      <button
                        key={template.name}
                        type="button"
                        onClick={() => {
                          setEditorMarkers([...template.markers])
                          setEditorName(template.name)
                          setEditorStartingFret(template.starting_fret)
                          setTemplateBrowserOpen(false)
                          setTemplateSearch('')
                        }}
                        className="rounded-md border border-gray-200 bg-white p-2 text-center hover:border-blue-400 hover:bg-blue-50"
                      >
                        <p className="mb-1 text-xs font-medium text-gray-900">
                          {template.name}
                        </p>
                        <div className="pointer-events-none">
                          <GuitarNeck
                            markers={template.markers}
                            stringCount={template.string_count}
                            tuning={template.tuning}
                            fretCount={5}
                            startingFret={template.starting_fret}
                          />
                        </div>
                      </button>
                    ))}
                </div>
              </div>
            )}
            <div className="mb-3 flex items-center gap-3">
              <span className="text-sm font-medium text-gray-700">
                Starting fret: {editorStartingFret}
              </span>
              <div className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={() =>
                    setEditorStartingFret((f) => Math.max(0, f - 1))
                  }
                  disabled={editorStartingFret <= 0}
                  className="flex h-8 w-8 items-center justify-center rounded-md border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-30"
                  aria-label="Decrease starting fret"
                >
                  −
                </button>
                <button
                  type="button"
                  onClick={() =>
                    setEditorStartingFret((f) => Math.min(19, f + 1))
                  }
                  disabled={editorStartingFret >= 19}
                  className="flex h-8 w-8 items-center justify-center rounded-md border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-30"
                  aria-label="Increase starting fret"
                >
                  +
                </button>
              </div>
            </div>
            <p className="mb-2 text-xs text-gray-500">
              Tap fret-string intersections to place or remove markers.
            </p>
            <GuitarNeck
              markers={editorMarkers}
              onMarkerToggle={handleMarkerToggle}
              fretCount={5}
              startingFret={editorStartingFret}
            />
            <div className="mt-4 flex justify-end gap-3">
              <button
                onClick={handleCancel}
                className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {saving ? 'Saving...' : 'Save'}
              </button>
            </div>
          </div>
        </div>
      )}

      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={handleDragEnd}
      >
        {chords.length === 0 && !editorOpen ? (
          <div className="rounded-lg border-2 border-dashed border-gray-300 p-8 text-center sm:p-12">
            <p className="text-gray-500">No chords yet.</p>
            <p className="mt-1 text-sm text-gray-400">
              Add your first chord to start building your progression.
            </p>
            <button
              onClick={openNewChordEditor}
              className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
            >
              Add Chord
            </button>
          </div>
        ) : (
          <>
            <SortableContext
              items={chords.map((c) => c.id)}
              strategy={verticalListSortingStrategy}
            >
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {chords.map((chord, index) => (
                  <SortableChordCard
                    key={chord.id}
                    chord={chord}
                    index={index}
                    total={chords.length}
                    onEdit={openEditChordEditor}
                    onDelete={handleDeleteChord}
                    onMoveUp={handleMoveUp}
                    onMoveDown={handleMoveDown}
                  />
                ))}
              </div>
            </SortableContext>
            <div className="mt-6">
              <button
                onClick={openNewChordEditor}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
              >
                Add Chord
              </button>
            </div>
          </>
        )}

        {/* Chord Sequence Section */}
        <div className="mt-8 border-t border-gray-200 pt-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-base font-semibold text-gray-900">
              Chord Sequence
            </h2>
            <div className="flex items-center gap-2">
              <button
                onClick={handleAddMeasure}
                className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                + Add Measure
              </button>
              <button
                onClick={handleSaveSequence}
                disabled={sequenceSaving}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {sequenceSaving ? 'Saving...' : 'Save Sequence'}
              </button>
            </div>
          </div>
          <ChordStaff
            numerator={sequenceNumerator}
            denominator={sequenceDenominator}
            measuresPerLine={measuresPerLine}
            measures={sequenceMeasures}
            chordMap={Object.fromEntries(chords.map((c) => [c.id, c.name ?? 'Untitled']))}
            onRemoveBeat={handleRemoveBeat}
            onRemoveMeasure={handleRemoveMeasure}
          />
        </div>
      </DndContext>

      {/* Toast notification */}
      {toast && (
        <div
          className={`fixed bottom-4 right-4 z-50 rounded-md px-4 py-2 text-sm font-medium text-white shadow-lg ${
            toast.type === 'success' ? 'bg-green-600' : 'bg-red-600'
          }`}
        >
          {toast.message}
        </div>
      )}
    </AppLayout>
  )
}
