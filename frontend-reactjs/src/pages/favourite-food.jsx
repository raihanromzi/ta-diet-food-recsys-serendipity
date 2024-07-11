import {Button} from "@/components/ui/button"
import {useNavigate} from "react-router-dom";

function FavouriteFood() {
    const navigate = useNavigate()

    return (<>
            <h2 className="text-3xl font-bold mb-4">Choose Your Favorite Foods!</h2>
            <p className={"font-sans text-sm font-medium"} style={{color: '#000'}}>Select at least 1 food you like.</p>
            <div className="form-responsive">
                <div className="grid mt-6 w-full items-center mr-6">
                    <img
                        src="https://images.unsplash.com/photo-1588345921523-c2dcdb7f1dcd?w=800&dpr=2&q=80"
                        alt="Photo by Drew Beamer"
                        className="rounded-md "
                    />
                </div>
                <div className="grid mt-6 w-full items-center">
                    <img
                        src="https://images.unsplash.com/photo-1588345921523-c2dcdb7f1dcd?w=800&dpr=2&q=80"
                        alt="Photo by Drew Beamer"
                        className="rounded-md "
                    />
                </div>
            </div>
            <div className="form-responsive">
                <div className="grid mt-6 w-full items-center mr-6">
                    <img
                        src="https://images.unsplash.com/photo-1588345921523-c2dcdb7f1dcd?w=800&dpr=2&q=80"
                        alt="Photo by Drew Beamer"
                        className="rounded-md "
                    />
                </div>
                <div className="grid mt-6 w-full items-center"></div>
            </div>
            <div className="flex mt-10 text-right justify-between">
                <Button variant="outline" className='rounded-full px-10' onClick={() => {
                    navigate("/")
                }}>Back</Button>
                <Button className='rounded-full bg-black px-10' onClick={() => {
                    navigate("/diet-food")
                }}>Get Your Diet Food</Button>
            </div>
        </>)
}

export default FavouriteFood
