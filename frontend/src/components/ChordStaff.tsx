import { useState } from 'react'
import { useDroppable } from '@dnd-kit/core'
import type { SequenceMeasure, SequenceBeat } from '../types/sequence'

export interface ChordStaffProps {
  numerator: number
  denominator: number
  measuresPerLine: number
  measures: SequenceMeasure[]
  chordMap: Record<string, string>
  onRemoveBeat: (measureId: string, beatPosition: number) => void
  onRemoveMeasure: (measureId: string) => void
}

function TimeSignature({ numerator, denominator }: { numerator: number; denominator: number }) {
  return (
    <div className="flex flex-col items-center justify-center px-2 text-center leading-none">
      <span className="text-xl font-bold text-gray-700">{numerator}</span>
      <span className="text-xl font-bold text-gray-700">{denominator}</span>
    </div>
  )
}

function BeatSlot({
  beat,
  measureId,
  chordMap,
  onRemoveBeat,
}: {
  beat: SequenceBeat
  measureId: string
  chordMap: Record<string, string>
  onRemoveBeat: (measureId: string, beatPosition: number) => void
}) {
  const [showMenu, setShowMenu] = useState(false)
  const { setNodeRef, isOver } = useDroppable({
    id: `beat|${measureId}|${beat.beat_position}`,
    data: { type: 'beat', measureId, beatPosition: beat.beat_position },
  })

  const chordName = beat.chord_id ? (chordMap[beat.chord_id] ?? 'Untitled') : null

  return (
    <div className="relative flex-1">
      {showMenu && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setShowMenu(false)} />
          <div className="absolute bottom-full left-1/2 z-20 mb-1 -translate-x-1/2 rounded border border-gray-200 bg-white shadow-md">
            <button
              type="button"
              onClick={() => {
                onRemoveBeat(measureId, beat.beat_position)
                setShowMenu(false)
              }}
              className="block w-full whitespace-nowrap px-3 py-1.5 text-left text-xs text-red-600 hover:bg-red-50"
            >
              Remove
            </button>
          </div>
        </>
      )}
      <div
        ref={setNodeRef}
        onClick={() => { if (beat.chord_id) setShowMenu((v) => !v) }}
        className={`flex h-12 w-full items-center justify-center rounded border text-xs transition-colors ${
          isOver
            ? 'border-blue-400 bg-blue-50'
            : beat.chord_id
              ? 'cursor-pointer border-gray-300 bg-white hover:border-gray-400'
              : 'border-dashed border-gray-300 bg-white text-gray-400'
        }`}
        aria-label={`Beat ${beat.beat_position}`}
      >
        {chordName === null ? (
          <span className="select-none opacity-50">—</span>
        ) : (
          <span className="font-medium text-gray-800">{chordName}</span>
        )}
      </div>
    </div>
  )
}

function Barline({ bold = false }: { bold?: boolean }) {
  return (
    <div
      className={`self-stretch ${bold ? 'w-1 bg-gray-700' : 'w-px bg-gray-400'}`}
    />
  )
}

function Measure({
  measure,
  chordMap,
  onRemoveBeat,
  onRemoveMeasure,
}: {
  measure: SequenceMeasure
  chordMap: Record<string, string>
  onRemoveBeat: (measureId: string, beatPosition: number) => void
  onRemoveMeasure: (measureId: string) => void
}) {
  const [confirmingRemove, setConfirmingRemove] = useState(false)
  const hasChords = measure.beats.some((b) => b.chord_id !== null)

  return (
    <div className="flex min-w-0 flex-1 flex-col gap-1 px-1">
      {/* Header row: ending bracket (left) + remove button (right) */}
      <div className="flex min-h-[1.25rem] items-center justify-between">
        {measure.ending_number !== null ? (
          <div className="border-l border-t border-gray-500 px-1 text-xs font-medium text-gray-600">
            {measure.ending_number}.
          </div>
        ) : (
          <div />
        )}
        {confirmingRemove ? (
          <span className="flex items-center gap-1 text-xs">
            <button
              type="button"
              onClick={() => { onRemoveMeasure(measure.id); setConfirmingRemove(false) }}
              className="rounded bg-red-600 px-1.5 py-0.5 text-white hover:bg-red-700"
            >
              Remove
            </button>
            <button
              type="button"
              onClick={() => setConfirmingRemove(false)}
              className="rounded border border-gray-300 px-1.5 py-0.5 text-gray-600 hover:bg-gray-50"
            >
              Cancel
            </button>
          </span>
        ) : (
          <button
            type="button"
            onClick={() => {
              if (hasChords) {
                setConfirmingRemove(true)
              } else {
                onRemoveMeasure(measure.id)
              }
            }}
            className="text-xs leading-none text-gray-400 hover:text-red-500"
            aria-label="Remove measure"
          >
            ×
          </button>
        )}
      </div>
      {/* Confirmation message */}
      {confirmingRemove && (
        <p className="text-xs text-red-600">This will remove all chords in this measure</p>
      )}
      {/* Beat slots */}
      <div className="flex gap-1">
        {measure.beats.map((beat) => (
          <BeatSlot
            key={beat.beat_position}
            beat={beat}
            measureId={measure.id}
            chordMap={chordMap}
            onRemoveBeat={onRemoveBeat}
          />
        ))}
      </div>
    </div>
  )
}

export default function ChordStaff({
  numerator,
  denominator,
  measuresPerLine,
  measures,
  chordMap,
  onRemoveBeat,
  onRemoveMeasure,
}: ChordStaffProps) {
  // Split measures into lines
  const lines: SequenceMeasure[][] = []
  for (let i = 0; i < measures.length; i += measuresPerLine) {
    lines.push(measures.slice(i, i + measuresPerLine))
  }

  return (
    <div className="space-y-3">
      {lines.map((lineMeasures, lineIndex) => (
        <div
          key={lineIndex}
          className="flex items-stretch overflow-x-auto rounded-md border border-gray-200 bg-gray-50 p-2"
        >
          {/* Time signature — only on first line */}
          {lineIndex === 0 && (
            <TimeSignature numerator={numerator} denominator={denominator} />
          )}

          {/* Opening barline */}
          <Barline />

          {lineMeasures.map((measure, measureIndex) => (
            <div key={measure.id} className="flex min-w-0 flex-1 items-stretch">
              <Measure
                measure={measure}
                chordMap={chordMap}
                onRemoveBeat={onRemoveBeat}
                onRemoveMeasure={onRemoveMeasure}
              />
              {/* Barline after each measure */}
              {measure.repeat_end ? (
                <>
                  <Barline />
                  <Barline bold />
                </>
              ) : measureIndex === lineMeasures.length - 1 ? (
                // Double barline at end of line
                <>
                  <Barline />
                  <Barline />
                </>
              ) : (
                <Barline />
              )}
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}
