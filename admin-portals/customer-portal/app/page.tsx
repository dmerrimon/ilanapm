import Image from "next/image";
import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-8 bg-white">
      <main className="flex flex-col items-center gap-8 max-w-2xl">
        <Image
          src="/logo.png"
          alt="Seleen Logo"
          width={300}
          height={80}
          priority
        />

        <h1 className="text-4xl md:text-5xl text-center">
          Customer Portal
        </h1>

        <p className="text-center text-lg opacity-80">
          Manage your Seleen licenses, users, and billing
        </p>

        <div className="flex gap-4 flex-col sm:flex-row">
          <Link
            href="/login"
            className="px-8 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors text-center"
          >
            Sign In
          </Link>
          <Link
            href="/dashboard"
            className="px-8 py-3 border border-black rounded-lg hover:bg-gray-50 transition-colors text-center"
          >
            Go to Dashboard
          </Link>
        </div>

        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
          <div className="p-6 border border-gray-200 rounded-lg">
            <h3 className="text-xl mb-2">License Management</h3>
            <p className="text-sm opacity-70">
              View your license status, activate seats, and manage user access
            </p>
          </div>

          <div className="p-6 border border-gray-200 rounded-lg">
            <h3 className="text-xl mb-2">Billing & Invoices</h3>
            <p className="text-sm opacity-70">
              Update payment methods, view invoices, and manage subscriptions
            </p>
          </div>

          <div className="p-6 border border-gray-200 rounded-lg">
            <h3 className="text-xl mb-2">Usage Analytics</h3>
            <p className="text-sm opacity-70">
              Track template generation, feedback submissions, and team activity
            </p>
          </div>
        </div>
      </main>

      <footer className="mt-16 text-sm opacity-50">
        <p>© 2026 Ilana Immersive LLC. All rights reserved.</p>
      </footer>
    </div>
  );
}
