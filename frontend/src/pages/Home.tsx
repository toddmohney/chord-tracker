import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4">
      <h1 className="text-3xl font-bold sm:text-4xl">Chord Tracker</h1>
      <p className="mt-2 text-center text-gray-500">
        Build, save, and organize guitar chord diagrams.
      </p>
      <div className="mt-6 flex gap-3">
        <Link
          to="/login"
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          Log In
        </Link>
        <Link
          to="/signup"
          className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Sign Up
        </Link>
      </div>
    </div>
  )
}
