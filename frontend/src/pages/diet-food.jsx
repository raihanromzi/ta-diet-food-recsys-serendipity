import {Button} from "@/components/ui/button"
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious
} from "@/components/ui/carousel"
import {Input} from "@/components/ui/input"
import {Label} from "@/components/ui/label"
import {useNavigate} from "react-router-dom";

function DietFood() {
  const navigate = useNavigate()

  return (
      <>
        <h2 className="text-3xl font-bold mb-4">Makanan Dietmu!</h2>
        <p className={"font-sans text-sm font-medium"}
           style={{color: '#000'}}>Please select foods for Breakfast,
          Dinner, and Lunch according to your calorie needs.</p>
        <div className="form-responsive mb-10">
          <div className="grid mt-6 w-full items-start mr-6">
            <div className="mb-4 text-xl font-semibold">BMI Calculator</div>
            <Input style={{borderColor: '#939393'}}
                   className="text-xl font-bold rounded-2xl border-2 text-center h-14"
                   defaultValue='40 Kg/m²'/>
            <div className={"font-sans text-sm font-medium mt-4"}
                 style={{color: '#000'}}>
              <div className="flex">
                <div>Status:</div>
                &nbsp;<b>Obesity</b>
              </div>
              <div className="flex">
                <div>BMI sehat:</div>
                &nbsp;<b>18.5 kg/m² - 25 kg/m²</b>
              </div>
            </div>
          </div>
          <div className="grid mt-6 w-full items-start">
            <div className="grid w-full items-center">
              <div className="mb-4 text-2xl font-semibold">Calorie Calculator
              </div>
              <div className={"font-sans text-sm font-medium -mt-4"}
                   style={{color: '#000'}}>
                <div className="flex">
                  <div>Maintaining Weight (TDEE):</div>
                  &nbsp;<b>343 Cal/day</b>
                </div>
                <div className="flex">
                  <div>Mild Weight Loss:</div>
                  &nbsp;<b>343 Cal/day</b>
                </div>
                <div className="flex">
                  <div>Maintaining Weight:</div>
                  &nbsp;<b>343 Cal/day</b>
                </div>
                <div className="flex">
                  <div>Extreme Weight Loss:</div>
                  &nbsp;<b>343 Cal/day</b>
                </div>
              </div>
            </div>
          </div>
        </div>
        <Label className={"font-sans text-2xl font-semibold"}>
          Breakfast
        </Label>
        <Carousel
            opts={{
              align: "start",
            }}
            className="w-full mt-4 mb-8"
        >
          <CarouselContent>
            {Array.from({length: 5}).map((_, index) => (
                <CarouselItem key={index} className="md:basis-1/2 lg:basis-1/3">
                  <div className="p-1">
                    <img
                        src="https://images.unsplash.com/photo-1588345921523-c2dcdb7f1dcd?w=800&dpr=2&q=80"
                        alt="Photo by Drew Beamer"
                        className="rounded-md "
                    />
                  </div>
                </CarouselItem>
            ))}
          </CarouselContent>
          <CarouselPrevious/>
          <CarouselNext/>
        </Carousel>
        <Label className={"font-sans text-2xl font-semibold"}>
          Lunch
        </Label>
        <Carousel
            opts={{
              align: "start",
            }}
            className="w-full mt-4 mb-8"
        >
          <CarouselContent>
            {Array.from({length: 5}).map((_, index) => (
                <CarouselItem key={index} className="md:basis-1/2 lg:basis-1/3">
                  <div className="p-1">
                    <img
                        src="https://images.unsplash.com/photo-1588345921523-c2dcdb7f1dcd?w=800&dpr=2&q=80"
                        alt="Photo by Drew Beamer"
                        className="rounded-md "
                    />
                  </div>
                </CarouselItem>
            ))}
          </CarouselContent>
          <CarouselPrevious/>
          <CarouselNext/>
        </Carousel>
        <Label className={"font-sans text-2xl font-semibold"}>
          Dinner
        </Label>
        <Carousel
            opts={{
              align: "start",
            }}
            className="w-full mt-4 mb-8"
        >
          <CarouselContent>
            {Array.from({length: 5}).map((_, index) => (
                <CarouselItem key={index} className="md:basis-1/2 lg:basis-1/3">
                  <div className="p-1">
                    <img
                        src="https://images.unsplash.com/photo-1588345921523-c2dcdb7f1dcd?w=800&dpr=2&q=80"
                        alt="Photo by Drew Beamer"
                        className="rounded-md "
                    />
                  </div>
                </CarouselItem>
            ))}
          </CarouselContent>
          <CarouselPrevious/>
          <CarouselNext/>
        </Carousel>
        <Label className={"font-sans text-2xl font-semibold"}>
          Snack (If Choose 5)
        </Label>
        <Carousel
            opts={{
              align: "start",
            }}
            className="w-full mt-4 mb-8"
        >
          <CarouselContent>
            {Array.from({length: 5}).map((_, index) => (
                <CarouselItem key={index} className="md:basis-1/2 lg:basis-1/3">
                  <div className="p-1">
                    <img
                        src="https://images.unsplash.com/photo-1588345921523-c2dcdb7f1dcd?w=800&dpr=2&q=80"
                        alt="Photo by Drew Beamer"
                        className="rounded-md "
                    />
                  </div>
                </CarouselItem>
            ))}
          </CarouselContent>
          <CarouselPrevious/>
          <CarouselNext/>
        </Carousel>
        <div className="flex mt-10 text-right justify-between">
          <Button variant="outline" className='rounded-full px-10'
                  onClick={() => {
                    navigate("/favourite-food")
                  }}>Back</Button>
          <Button className='rounded-full bg-black px-10' onClick={() => {
            navigate("/time-to-eat")
          }}>Create Plan</Button>
        </div>
      </>
  )
}

export default DietFood
