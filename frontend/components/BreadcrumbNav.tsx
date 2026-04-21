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
      <ol className="flex items-center gap-1.5 text-sm text-b1-dark flex-wrap">
        <li>
          <Link href="/" className="hover:text-b1-darker transition-colors">
            Home
          </Link>
        </li>
        {crumbs.map((crumb, i) => (
          <li key={i} className="flex items-center gap-1.5">
            <span className="text-b1-light">/</span>
            {i === crumbs.length - 1 ? (
              <span className="text-b1-darker font-medium">{crumb.name}</span>
            ) : (
              <Link href={crumb.href} className="hover:text-b1-darker transition-colors">
                {crumb.name}
              </Link>
            )}
          </li>
        ))}
      </ol>
    </nav>
  )
}
