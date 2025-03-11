import React, {Fragment, useState, useEffect, useContext, createContext} from 'react'
import ReactDOM from 'react-dom'
import {
  BrowserRouter as Router,
  Route,
  Switch,
  Redirect,
} from 'react-router-dom'

import './style.css'
import Login from './views/login'
import SignUp from './views/signup'
import GuestHome from './views/guest-home'

import NotFound from './views/not-found'

export const  CurrentUserContext = createContext(null);

const App = () => {

  const [currentUser, setCurrentUser] = useState(null);


  return (

      <CurrentUserContext.Provider
          value={{
            currentUser,
            setCurrentUser
          }}
       >
    <Router>
      <Switch>
          <Route component={Login} exact path="/" />
          <Route component={SignUp} exact path="/signup" />
          <Route component={GuestHome} exact path="/guest"/>
          
          <Route component={NotFound} path="**" />
          <Redirect to="**" />
      </Switch>
    </Router>
</CurrentUserContext.Provider>
  )

}


ReactDOM.render(<App />, document.getElementById('app'))
