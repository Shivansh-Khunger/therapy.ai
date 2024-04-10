import React from 'react'
import Header from './Header'
import back from "./Assest/052.jpg"
import yoga from "./Assest/yoga.png"
import { Link } from 'react-router-dom'
const Home = () => {
  return (
    <div className="Home">
      {/* <Header /> */}
      <div className="back">
        <img className="backdrop" src={back} alt="" />
        <div className="header">
          <div className="links">
            <Link to={"/"}>
              <div className="each-nod">Home</div>
            </Link>
            <Link to={"/phy"}>
              <div className="each-nod">Contact us</div>
            </Link>
            <Link to={"/"}>
              <div className="each-nod">About us</div>
            </Link>
          </div>
        </div>

        <img className="yoga" src={yoga} alt="" />
      </div>
      <div className="but">
        <button>Get Started</button>
      </div>
      <div className="yoga"></div>
    </div>
  );
}

export default Home