import type {Metadata} from 'next';
import './globals.css';
export const metadata:Metadata={title:'Orbit Watch · Your 45 km satellite tracker',description:'Track satellite ground positions around your location and connect Telegram pass alerts.',icons:{icon:'/favicon.svg'}};
export default function RootLayout({children}:Readonly<{children:React.ReactNode}>){return <html lang="en"><body>{children}</body></html>;}
