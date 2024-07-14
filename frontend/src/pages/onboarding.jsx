import {useState} from "react"
import {Input} from "@/components/ui/input"
import {Label} from "@/components/ui/label"
import {Button} from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {useNavigate} from "react-router-dom";

function Onboarding() {

  const [age, setAge] = useState('18')
  const [weight, setWeight] = useState('60')
  const [height, setHeight] = useState('170')
  const [gender, setGender] = useState('Male')
  const [activityLevel, setActivityLevel] = useState('Moderately')
  const [numberOfMealsPerDay, setNumberOfMealsPerDay] = useState('3')
  const navigate = useNavigate()

  const handleNextClick = () => {
    navigate("/favourite-food")
  };

  return (<>
    <h2 className="text-3xl font-sans font-bold mb-4">Welcome!</h2>
    <p className={"font-sans text-sm font-medium"} style={{color: '#000'}}>Enter
      your Age, Weight, Gender,
      Activity Level, and Number of meals per day so
      we can suggest a suitable diet for you.</p>
    <div className="form-responsive">
      <div className="grid mt-10 w-full items-center mr-6">
        <Label htmlFor="umur" className='mb-4'>Age</Label>
        <Input type="number" id="age" placeholder={age}
               onChangeCapture={(e) => setAge(e.currentTarget.value)}/>
      </div>
      <div className="grid mt-10 w-full items-center">
        <Label htmlFor="weight" className='mb-4'>Weight</Label>
        <Input type="number" id="weight" placeholder={weight}
               onChangeCapture={(e) => setWeight(e.currentTarget.value)}/>
      </div>
    </div>
    <div className="form-responsive">
      <div className="grid mt-10 w-full items-center mr-6">
        <Label htmlFor="height" className='mb-4'>Height</Label>
        <Input type="number" id="height" placeholder={height}
               onChangeCapture={(e) => setHeight(e.currentTarget.value)}/>
      </div>
      <div className="grid mt-10 w-full items-center">
        <Label className='mb-4'>Gender</Label>
        <Select className="w-full" onValueChange={(e) => setGender(e)}>
          <SelectTrigger>
            <SelectValue placeholder={gender}/>
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectItem value="male">Male</SelectItem>
              <SelectItem value="female">Female</SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>
    </div>
    <div className="form-responsive">
      <div className="grid mt-10 w-full items-center">
        <Label htmlFor="activityLevel" className='mb-4'>Activity level</Label>
        <Select className="w-full" onValueChange={(e) => setActivityLevel(e)}>
          <SelectTrigger>
            <SelectValue placeholder={activityLevel}/>
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectItem value="never">Never</SelectItem>
              <SelectItem value="lightly">Lightly</SelectItem>
              <SelectItem value="moderately">Moderately</SelectItem>
              <SelectItem value="very-active">Very Active</SelectItem>
              <SelectItem value="extra-active">Extra Active</SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>
    </div>
    <div>
      <div className="grid mt-10 w-full items-center">
        <Label className='mb-4'>Number of Meals per Day</Label>
        <Select className="w-full"
                onValueChange={(e) => setNumberOfMealsPerDay(e)}>
          <SelectTrigger>
            <SelectValue placeholder={numberOfMealsPerDay}/>
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectItem value="3">3</SelectItem>
              <SelectItem value="5">5</SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>
    </div>
    <div className="mt-10 text-right">
      <Button className='rounded-full bg-black px-10'
              onClick={handleNextClick}>Next</Button>
    </div>
  </>)
}

export default Onboarding
