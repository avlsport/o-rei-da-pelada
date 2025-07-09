import React from 'react';
import PropTypes from 'prop-types';
import logo from '../../assets/logo_rei_da_pelada.png';
import background from '../../assets/background.jpeg';

const AuthLayout = ({ children }) => {
  return (
    <div
      className="min-h-screen flex items-center justify-center bg-cover bg-center relative"
      style={{ backgroundImage: `url(${background})` }}
    >
      <div className="absolute inset-0 bg-black opacity-70"></div>
      <div className="relative z-10 p-8 rounded-lg shadow-lg text-center glass-effect max-w-md w-full mx-4">
        <img src={logo} alt="O Rei da Pelada Logo" className="mx-auto mb-6 w-24 h-24" />
        <h1 className="text-4xl font-bold text-white mb-2 gradient-text">
          O Rei da Pelada
        </h1>
        <p className="text-xl text-gray-300 mb-8">
          Sua pelada em outro nível
        </p>
        {children}
      </div>
    </div>
  );
};

AuthLayout.propTypes = {
  children: PropTypes.node.isRequired,
};

export default AuthLayout;


