import './globals.css'
import Navbar from '../components/Navbar'

export const metadata = {
  title: 'Placement Readiness Analyzer',
  description: 'AI-driven placement prediction and skill gap analysis',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        {children}
      </body>
    </html>
  )
}
