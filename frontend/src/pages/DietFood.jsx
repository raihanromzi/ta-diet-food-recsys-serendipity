import { Button } from '@/components/ui/Button.jsx';
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from '@/components/ui/Carousel.jsx';
import { Input } from '@/components/ui/Input.jsx';
import { Label } from '@/components/ui/Label.jsx';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';

function DietFood() {
  const navigate = useNavigate();

  // Accessing the state from Redux
  const { bmi, tdee, bmiStatus, breakfast, lunch, dinner } = useSelector(
    state => state.user
  );

  return (
    <>
      <h2 className='text-3xl font-bold mb-4'>Choose Your Diet Food!</h2>
      <p className={'font-sans text-sm font-medium'} style={{ color: '#000' }}>
        Please select foods for Breakfast, Dinner, and Lunch according to your
        calorie needs.
      </p>
      <div className='form-responsive mb-10'>
        <div className='grid mt-6 w-full items-start mr-6'>
          <div className='mb-4 text-xl font-semibold'>BMI Calculator</div>
          <Input
            style={{ borderColor: '#939393' }}
            className='text-xl font-bold rounded-2xl border-2 text-center h-14'
            value={`${bmi.toFixed(2)} Kg/m²`}
            readOnly
          />
          <div
            className={'font-sans text-sm font-medium mt-4'}
            style={{ color: '#000' }}
          >
            <div className='flex'>
              <div>Status:</div>
              &nbsp;<b>{bmiStatus}</b>
            </div>
            <div className='flex'>
              <div>BMI sehat:</div>
              &nbsp;<b>18.5 kg/m² - 25 kg/m²</b>
            </div>
          </div>
        </div>
        <div className='grid mt-6 w-full items-start'>
          <div className='grid w-full items-center'>
            <div className='mb-4 text-2xl font-semibold'>
              Calorie Calculator
            </div>
            <div
              className={'font-sans text-sm font-medium -mt-4'}
              style={{ color: '#000' }}
            >
              <div className='flex mb-4'>
                <div>Calories need to maintain weight</div>
              </div>

              <div className='flex'>
                <div>Maintaining Weight (TDEE):</div>
                &nbsp;<b>{tdee} Cal/day</b>
              </div>
            </div>
          </div>
        </div>
      </div>
      <Label className={'font-sans text-2xl font-semibold'}>Breakfast</Label>
      <Carousel
        opts={{
          align: 'start',
        }}
        className='w-full mt-4 mb-8'
      >
        <CarouselContent>
          {breakfast.map((food, index) => (
            <CarouselItem key={index} className='md:basis-1/2 lg:basis-1/3'>
              <div className='p-1'>
                <img
                  src={food.ImageLink}
                  alt={food.NameClean}
                  className='rounded-md '
                />
                <p className='text-center'>{food.NameClean}</p>
                <p className='text-center'>{food.Calories} Cal</p>
              </div>
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselPrevious />
        <CarouselNext />
      </Carousel>
      <Label className={'font-sans text-2xl font-semibold'}>Lunch</Label>
      <Carousel
        opts={{
          align: 'start',
        }}
        className='w-full mt-4 mb-8'
      >
        <CarouselContent>
          {lunch.map((food, index) => (
            <CarouselItem key={index} className='md:basis-1/2 lg:basis-1/3'>
              <div className='p-1'>
                <img
                  src={food.ImageLink}
                  alt={food.NameClean}
                  className='rounded-md '
                />
                <p className='text-center'>{food.NameClean}</p>
                <p className='text-center'>{food.Calories} Cal</p>
              </div>
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselPrevious />
        <CarouselNext />
      </Carousel>
      <Label className={'font-sans text-2xl font-semibold'}>Dinner</Label>
      <Carousel
        opts={{
          align: 'start',
        }}
        className='w-full mt-4 mb-8'
      >
        <CarouselContent>
          {dinner.map((food, index) => (
            <CarouselItem key={index} className='md:basis-1/2 lg:basis-1/3'>
              <div className='p-1'>
                <img
                  src={food.ImageLink}
                  alt={food.NameClean}
                  className='rounded-md '
                />
                <p className='text-center'>{food.NameClean}</p>
                <p className='text-center'>{food.Calories} Cal</p>
              </div>
            </CarouselItem>
          ))}
        </CarouselContent>
        <CarouselPrevious />
        <CarouselNext />
      </Carousel>

      <div className='flex mt-10 text-right justify-between'>
        <Button
          variant='outline'
          className='rounded-full px-10'
          onClick={() => {
            navigate('/favourite-food');
          }}
        >
          Back
        </Button>
        <Button
          className='rounded-full bg-black px-10'
          onClick={() => {
            navigate('/time-to-eat');
          }}
        >
          Create Plan
        </Button>
      </div>
    </>
  );
}

export default DietFood;
