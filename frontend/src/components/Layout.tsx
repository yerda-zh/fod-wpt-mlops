import { NavLink } from "react-router-dom";

interface LayoutProps {
  children: React.ReactNode;
}

const navLinks = [
  { to: "/", label: "Predict" },
  { to: "/history", label: "History" },
  { to: "/monitoring", label: "Monitoring" },
];

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
        <span className="text-lg font-semibold text-gray-900">FOD-WPT</span>
        <div className="flex gap-6">
          {navLinks.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                isActive
                  ? "text-sm font-medium text-blue-600"
                  : "text-sm font-medium text-gray-500 hover:text-gray-900"
              }
            >
              {label}
            </NavLink>
          ))}
        </div>
      </nav>
      <main className="max-w-5xl mx-auto px-6 py-8">{children}</main>
    </div>
  );
}
