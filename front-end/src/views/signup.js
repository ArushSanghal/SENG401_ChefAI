import React, { Fragment, useState, useEffect } from 'react'

import { Helmet } from 'react-helmet'

import Footer41 from '../components/footer41'
import './home.css'
import SignUp2 from '../components/sign-up2'

const SignUp = (props) => {

  const [members, setMembers] = useState(null);
  const [admins, setAdmins] = useState(null);


  return (
    <div className="blog-container thq-section-padding">
      <Helmet>
        <title>ChefAI</title>
        <meta property="og:title" content="ChefAI" />
      </Helmet>

    <SignUp2
    ></SignUp2>


    </div>
  )
}


function checkCredentials (usernameCheck, passwordCheck){
    
}



export default SignUp
