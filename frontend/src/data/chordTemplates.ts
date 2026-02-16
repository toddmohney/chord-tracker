export interface ChordTemplate {
  name: string
  markers: { string: number; fret: number }[]
  string_count: number
  tuning: string
}

// Standard 6-string guitar tuning (EADGBE)
// Strings numbered 0 (low E) to 5 (high E), frets 1-5
export const chordTemplates: ChordTemplate[] = [
  {
    name: 'A',
    markers: [
      { string: 3, fret: 2 },
      { string: 2, fret: 2 },
      { string: 1, fret: 2 },
    ],
    string_count: 6,
    tuning: 'EADGBE',
  },
  {
    name: 'Am',
    markers: [
      { string: 3, fret: 2 },
      { string: 2, fret: 2 },
      { string: 1, fret: 1 },
    ],
    string_count: 6,
    tuning: 'EADGBE',
  },
  {
    name: 'B',
    markers: [
      { string: 4, fret: 2 },
      { string: 3, fret: 4 },
      { string: 2, fret: 4 },
      { string: 1, fret: 4 },
      { string: 0, fret: 2 },
      { string: 5, fret: 2 },
    ],
    string_count: 6,
    tuning: 'EADGBE',
  },
  {
    name: 'Bm',
    markers: [
      { string: 4, fret: 2 },
      { string: 3, fret: 4 },
      { string: 2, fret: 4 },
      { string: 1, fret: 3 },
      { string: 0, fret: 2 },
      { string: 5, fret: 2 },
    ],
    string_count: 6,
    tuning: 'EADGBE',
  },
  {
    name: 'C',
    markers: [
      { string: 4, fret: 3 },
      { string: 3, fret: 2 },
      { string: 1, fret: 1 },
    ],
    string_count: 6,
    tuning: 'EADGBE',
  },
  {
    name: 'D',
    markers: [
      { string: 3, fret: 2 },
      { string: 2, fret: 3 },
      { string: 1, fret: 2 },
    ],
    string_count: 6,
    tuning: 'EADGBE',
  },
  {
    name: 'Dm',
    markers: [
      { string: 3, fret: 2 },
      { string: 2, fret: 3 },
      { string: 1, fret: 1 },
    ],
    string_count: 6,
    tuning: 'EADGBE',
  },
  {
    name: 'E',
    markers: [
      { string: 4, fret: 2 },
      { string: 3, fret: 2 },
      { string: 2, fret: 1 },
    ],
    string_count: 6,
    tuning: 'EADGBE',
  },
  {
    name: 'Em',
    markers: [
      { string: 4, fret: 2 },
      { string: 3, fret: 2 },
    ],
    string_count: 6,
    tuning: 'EADGBE',
  },
  {
    name: 'F',
    markers: [
      { string: 4, fret: 3 },
      { string: 3, fret: 3 },
      { string: 2, fret: 2 },
      { string: 1, fret: 1 },
      { string: 0, fret: 1 },
      { string: 5, fret: 1 },
    ],
    string_count: 6,
    tuning: 'EADGBE',
  },
  {
    name: 'G',
    markers: [
      { string: 4, fret: 3 },
      { string: 0, fret: 3 },
      { string: 5, fret: 3 },
      { string: 3, fret: 2 },
    ],
    string_count: 6,
    tuning: 'EADGBE',
  },
]
