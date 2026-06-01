import { BrowserRouter, Routes, Route } from 'react-router-dom'
import AdminLayout from './layouts/AdminLayout'

import AdminDashboard from './pages/AdminDashboard'
import QuizList from './pages/QuizList'
import Students from './pages/Students'
import Leaderboard from './pages/Leaderboard'
import Excel from './pages/Excel'
import NotFound from './pages/NotFound'
import IndexRedirect from './pages/IndexRedirect'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AdminLayout />}>
          <Route path="/" element={<AdminDashboard />} />
          <Route path="/quizzes" element={<QuizList />} />
          <Route path="/students" element={<Students />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route path="/excel" element={<Excel />} />

          {/* Safety redirect */}
          <Route path="/index" element={<IndexRedirect />} />

          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
