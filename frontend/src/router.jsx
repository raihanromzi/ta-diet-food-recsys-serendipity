import {Route, Routes} from 'react-router-dom';
import Sidebar from './components/sidebar'
import Onboarding from "./pages/onboarding";
import FavouriteFood from "./pages/favourite-food";
import NotFound from './pages/not-found';
import DietFood from './pages/diet-food';
import TimeToEat from './pages/time-to-eat';

function Router() {
  return (
      <div>
        <Sidebar>
          <Routes>
            <Route path="/" element={<Onboarding/>}/>
            <Route path="favourite-food" element={<FavouriteFood/>}/>
            <Route path="diet-food" element={<DietFood/>}/>
            <Route path="time-to-eat" element={<TimeToEat/>}/>
            <Route path="*" element={<NotFound/>}/>
          </Routes>
        </Sidebar>
      </div>
  )
}

export default Router
