'use client';

import Image from "next/image";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { clearAccessToken } from "@/lib/api-client";

export default function Header() {
  const router = useRouter();
  const pathname = usePathname();

  const handleSignOut = () => {
    clearAccessToken();
    router.push("/login");
  };

  const navLinks = [
    { href: "/dashboard", label: "Dashboard" },
    { href: "/customers", label: "Customers" },
    { href: "/users", label: "Users" },
    { href: "/devices", label: "Devices" },
    { href: "/licenses", label: "Licenses" },
    { href: "/analytics", label: "Analytics" },
    { href: "/settings", label: "Settings" },
  ];

  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/dashboard">
              <Image
                src="/logo.png"
                alt="Seleen Logo"
                width={120}
                height={32}
                priority
              />
            </Link>
            <nav className="flex gap-6">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={
                    pathname === link.href || pathname?.startsWith(link.href + "/")
                      ? "text-black font-medium"
                      : "text-gray-600 hover:text-black transition-colors"
                  }
                >
                  {link.label}
                </Link>
              ))}
            </nav>
          </div>
          <button
            onClick={handleSignOut}
            className="px-4 py-2 text-gray-600 hover:text-black transition-colors"
          >
            Sign Out
          </button>
        </div>
      </div>
    </header>
  );
}
