import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './router.jsx'
import '../app/globals.css'
import './scss/index.scss'
import {BrowserRouter} from 'react-router-dom'

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <BrowserRouter>
            <App/>
        </BrowserRouter>
    </React.StrictMode>,
)
