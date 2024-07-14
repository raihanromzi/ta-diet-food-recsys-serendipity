import { Button } from '@/components/ui/Button.jsx';
import { useNavigate } from 'react-router-dom';

function TimeToEat() {
  const navigate = useNavigate();

  return (
    <>
      <h2 className='text-3xl font-bold mb-4'>Time to Eat!</h2>
      <p className={'font-sans text-sm font-medium'} style={{ color: '#000' }}>
        Here are the foods you have selected and a comparison of calories with
        what you need.
      </p>
      <div className='form-responsive'>
        <div className='grid mt-6 w-full items-start mr-6'>
          <div className='mb-4 text-xl font-semibold'>Breakfast</div>
          <img
            src='https://images.unsplash.com/photo-1588345921523-c2dcdb7f1dcd?w=800&dpr=2&q=80'
            alt='Photo by Drew Beamer'
            className='rounded-md '
          />
        </div>
        <div className='grid mt-6 w-full items-start mr-6'>
          <div className='mb-4 text-xl font-semibold'>Lunch</div>
          <img
            src='https://images.unsplash.com/photo-1588345921523-c2dcdb7f1dcd?w=800&dpr=2&q=80'
            alt='Photo by Drew Beamer'
            className='rounded-md '
          />
        </div>
      </div>
      <div className='form-responsive'>
        <div className='grid mt-6 w-full items-start mr-6'>
          <div className='mb-4 text-xl font-semibold'>Dinner</div>
          <img
            src='https://images.unsplash.com/photo-1588345921523-c2dcdb7f1dcd?w=800&dpr=2&q=80'
            alt='Photo by Drew Beamer'
            className='rounded-md '
          />
        </div>
        <div className='grid mt-6 w-full items-start mr-6'></div>
      </div>
      <div className='form-responsive'>
        <div className='grid mt-6 w-full items-start mr-6'>
          <div className='grid w-full items-start'>
            <div className='grid w-full items-center'>
              <div className='mb-4 text-xl font-semibold'>
                Calorie Calculator
              </div>
              <div
                className={'font-sans text-sm font-medium -mt-4'}
                style={{ color: '#000' }}
              >
                <div className='flex'>
                  <div>Recommended daily calories:</div>
                  &nbsp;<b>343 Cal/day</b>
                </div>
                <div className='flex'>
                  <div>Calories from selected foods:</div>
                  &nbsp;<b>343 Cal/day</b>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className='flex mt-10 text-right justify-between'>
        <Button
          variant='outline'
          className='rounded-full px-10'
          onClick={() => {
            navigate('/diet-food');
          }}
        >
          Back
        </Button>
        {/*<Button className='rounded-full bg-black px-10'>Finish!</Button>*/}
      </div>
    </>
  );
}

export default TimeToEat;
