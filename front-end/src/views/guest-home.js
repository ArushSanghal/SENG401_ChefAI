import React, { Fragment, useState, useEffect } from 'react'

import { Helmet } from 'react-helmet'

import Footer41 from '../components/footer41'
import './home.css'
import NavBar8 from '../components/navbar8'
import FoodForm  from '../components/food-form'

const GuestHome = (props) => {

  const [members, setMembers] = useState(null);
  const [admins, setAdmins] = useState(null);


  return (
    <div className="blog-container">
      <Helmet>
        <title>ChefAI</title>
        <meta property="og:title" content="ChefAI" />
      </Helmet>

    <NavBar8
    ></NavBar8>

    <FoodForm>   
    </FoodForm>

    </div>
  )
}


function checkCredentials (usernameCheck, passwordCheck){
    
}



export default GuestHome
