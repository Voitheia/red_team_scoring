import { Link } from 'react-router-dom'
import '../styles/App.css'


type NavbarProps = {
  admin: boolean;
};


const Navbar: React.FC<NavbarProps> = ({ admin }) => {
  return (
    <section className='navbar-container'>
        <ul className='navbar-list'>
          { admin ? 
            <li className='navbar-item'><Link to="/">Home</Link></li>
          :
            <li className='navbar-item'><Link to="/admin">Admin</Link></li>
            }
            <li className='navbar-item'><Link to="/login">Login</Link></li>
        </ul>
    </section>
  )
}

export default Navbar
