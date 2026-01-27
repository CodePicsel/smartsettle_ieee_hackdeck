package com.example.splitexpense;

import android.os.Bundle;

import androidx.fragment.app.Fragment;

import android.telecom.Call;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;

import javax.security.auth.callback.Callback;

public class PhoneNumberFragment extends Fragment {
    EditText et_phone;
    Button btn_send_otp;

    public PhoneNumberFragment() { }

    public static PhoneNumberFragment newInstance() {
        return new PhoneNumberFragment();
    }

//    @Override
//    public void onCreate(Bundle savedInstanceState) {
//        super.onCreate(savedInstanceState);
//
//    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_phone_number, container, false);
        // Inflate the layout for this fragment
        et_phone = view.findViewById(R.id.et_phone);
        btn_send_otp = view.findViewById(R.id.btn_send_otp);

        btn_send_otp.setOnClickListener(v -> {
            String phone = et_phone.getText().toString().trim();

            if (phone.isEmpty() || phone.length() < 10) {
                et_phone.setError("Enter valid phone number");
                return;
            }

            // 🔹 Move to OTP screen immediately
            VerifyOtpFragment fragment = new VerifyOtpFragment();
            Bundle bundle = new Bundle();
            bundle.putString("phone", phone);
            fragment.setArguments(bundle);

            getParentFragmentManager().beginTransaction()
                    .replace(R.id.auth_fragment_container, fragment)
                    .addToBackStack(null)
                    .commit();

            // 🔹 Send OTP API in background
            //sendOtpToBackend(phone);});
        });
        return view;
    }
}