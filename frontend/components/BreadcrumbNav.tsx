import Link from 'next/link'

interface Crumb {
  name: string
  href: string
}

interface BreadcrumbNavProps {
  crumbs: Crumb[]
}

export default function BreadcrumbNav({ crumbs }: BreadcrumbNavProps) {
  return (
    <nav aria-label="Breadcrumb" className="mb-6">
      <ol className="flex items-center gap-1.5 text-sm text-gray-500 flex-wrap">
        <li>
          <Link href="/" className="hover:text-gray-900">
            Home
          </Link>
        </li>
        {crumbs.map((crumb, i) => (
          <li key={i} className="flex items-center gap-1.5">
            <span className="text-gray-300">/</span>
            {i === crumbs.length - 1 ? (
              <span className="text-gray-900 font-medium">{crumb.name}</span>
            ) : (
              <Link href={crumb.href} className="hover:text-gray-900">
                {crumb.name}
              </Link>
            )}
          </li>
        ))}
      </ol>
    </nav>
  )
}
