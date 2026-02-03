import { useEffect, useState } from "react";
import logo from '../assets/logo.png'
import { useDispatch } from "react-redux";
import { Link, useNavigate } from "react-router-dom";
import {login as authLogin} from '../app/authSlice'

function Login() {
    const navigate = useNavigate()
    const dispatch = useDispatch();
    const [phone, setPhone] = useState("");
    const [showOtp, setShowOtp] = useState(false);
    const [otp, setOtp] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const [resendCooldown, setResendCooldown] = useState(0);
    
  // Phone input handler
  const handlePhoneChange = (e) => {
    const value = e.target.value.replace(/\D/g, "");
    if (value.length > 10) return;
    setPhone(value);
    setError("");
  };

  // Send OTP
  const sendOtp = async () => {
    if (!/^[1-9]\d{9}$/.test(phone)) {
      setError("Enter a valid 10-digit phone number");
      return;
    }

    setLoading(true);
    const fullPhone = `+91${phone}`;

    try {
      const res = await fetch("http://localhost:8000/auth/request-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phone: fullPhone })
      });

      const data = await res.json();

      if (data.otp_sent) {
        setShowOtp(true);
        startResendCooldown();
      } else {
        setError("Failed to send OTP");
      }
    } catch {
      setError("Server error");
    } finally {
      setLoading(false);
    }
  };

  // Verify OTP
  const verifyOtp = async () => {
    if (otp.length !== 6) {
      setError("Enter 6-digit OTP");
      return;
    }

    try {
      const res = await fetch("http://localhost:8000/auth/verify-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          phone: `+91${phone}`,
          otp
        })
      });

      const data = await res.json();

      if (data.ok) {
        // if(data.user_exists) {
        //   sessionStorage.setItem("access_token", data.access_token);
        //   console.log('user Exists')
        //   navigate('/home')
        //   console.log(data)
        //   dispatch(authLogin({status: true}))
        // }
      if (data.user_exists) {
      sessionStorage.setItem("access_token", data.access_token);

      dispatch(
        authLogin({
          status: true,
          userData: data.user 
          })
        );

          navigate("/");
        }
        else{
          sessionStorage.setItem("temp_token", data.temp_token);
          console.log("Sent to register");
          navigate('/register')
        }
        
      } else {
        setError("Invalid OTP");
      }
    } catch {
      setError("OTP verification failed");
    }
  };

  // Resend cooldown
  const startResendCooldown = () => {
    setResendCooldown(30);
    const timer = setInterval(() => {
      setResendCooldown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const onkeydown = (fn) => (e) => {
    if(e.key === "Enter"){
      fn(e)
    }
  }

  return (
    <div className="login-card flex flex-col rounded-lg p-4 items-center border-2 w-80 text-center bg-gray-100 shadow-red-900 ">
      <div className="img-cont">
        <img src={logo} className="w-full" />
      </div>
      <hr className="login-hr mt-2 rounded-full border-black w-full" />
      {/* PHONE INPUT */}
      <div className="text-[1.2rem] flex gap-1 border  p-2 m-2 rounded-lg w-full bg-blue-200 font-[poppins-lt]" >
        <span>+91 </span>
        <input
          id="phone"
          type="tel"
          value={phone}
          onChange={handlePhoneChange}
          placeholder="9876543210"
          disabled={showOtp}
          onKeyDown={onkeydown(sendOtp)}
        />
      </div>

      {!showOtp && (
        <button onClick={sendOtp} disabled={loading} className="border-2 border-blue-900 bg-blue-600 rounded-lg text-white font-[poppins-sb] p-2 m-2 w-full">
          {loading ? "Sending..." : "Send OTP"}
        </button>
      )}

      {/* OTP SECTION */}
      {showOtp && (
        <>
          <input
            id="otp"
            type="text"
            placeholder="Enter OTP"
            value={otp}
            onChange={(e) =>
              setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))
            }
            onKeyDown={onkeydown(verifyOtp)}
            className="text-[1.2rem] flex gap-1 border  p-2 m-2 rounded-lg w-full bg-blue-200 outline font-[poppins-lt]"
          />
        <div className="flex w-full">
          <button 
          onClick={verifyOtp}
          className="border-2 p-2 m-2 w-full font-[poppins-sb] rounded-lg border-blue-900 bg-blue-600 text-white cursor-pointer"
          >Verify OTP</button>

          <button
            onClick={sendOtp}
            disabled={resendCooldown > 0}
            style={{ marginTop: "8px" }}
            className={`border p-2 m-2 w-full font-[poppins-sb]  rounded-lg ${resendCooldown > 0 ? 'bg-gray-200 cursor-not-allowed' : 'bg-white cursor-pointer'}`}
          >
            {resendCooldown > 0
              ? `Resend OTP ${resendCooldown}s`
              : "Resend OTP"}
          </button>
        </div>
        </>
      )}

      {/* <Link to={'/auth/register'}>Register</Link> */}
      {/* <h5 className="text-[0.8rem] font-[poppins-sb] hover:underline hover:text-blue-600 cursor-pointer">register</h5> */}

      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default Login;
