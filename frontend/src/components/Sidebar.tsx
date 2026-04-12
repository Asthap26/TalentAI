'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';

export default function Sidebar() {
  const pathname = usePathname();

  const menuItems = [
    {
      name: 'Parsed Data',
      path: '/',
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
          <line x1="16" y1="13" x2="8" y2="13"></line>
          <line x1="16" y1="17" x2="8" y2="17"></line>
          <polyline points="10 9 9 9 8 9"></polyline>
        </svg>
      ),
    },
    {
      name: 'Candidate Matching',
      path: '/matching',
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
          <circle cx="9" cy="7" r="4"></circle>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
        </svg>
      ),
    },
  ];

  return (
    <ul className="sidebar-menu">
      {menuItems.map((item) => (
        <li 
          key={item.path} 
          className={`sidebar-item ${pathname === item.path ? 'active' : ''}`}
        >
          <Link 
            href={item.path} 
            style={{
              display: 'flex', 
              alignItems: 'center', 
              gap: '12px', 
              textDecoration: 'none', 
              color: 'inherit', 
              width: '100%'
            }}
          >
            {item.icon}
            {item.name}
          </Link>
        </li>
      ))}
    </ul>
  );
}
