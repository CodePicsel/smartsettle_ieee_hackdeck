package com.example.splitexpense.fragments;

import android.os.Bundle;

import androidx.fragment.app.Fragment;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.example.splitexpense.models.SendOtpRequest;
import com.example.splitexpense.network.ApiClient;
import com.example.splitexpense.network.ApiService;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;


import com.example.splitexpense.R;

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

        btn_send_otp.setOnClickListener(v ->{

            String phone = et_phone.getText().toString().trim();

            if (phone.isEmpty() || phone.length() < 10) {
                et_phone.setError("Enter valid phone number");
                return;
            }

            if(!phone.startsWith("+91")) {
                phone = "+91" + phone;
            }

            sendOtpToBackend(phone);
        });
        return view;
    }
    private void sendOtpToBackend(String phone) {

        ApiService apiService = ApiClient.getClient().create(ApiService.class);
        SendOtpRequest request = new SendOtpRequest(phone);

        apiService.requestOtp(request).enqueue(new Callback<Void>() {
            @Override
            public void onResponse(Call<Void> call, Response<Void> response) {

                if(response.isSuccessful()) {
                    // Move to OTP screen
                    VerifyOtpFragment fragment = new VerifyOtpFragment();
                    Bundle bundle = new Bundle();
                    bundle.putString("phone", phone);
                    fragment.setArguments(bundle);

                    getParentFragmentManager().beginTransaction()
                            .replace(R.id.auth_fragment_container, fragment)
                            .addToBackStack(null)
                            .commit();
                } else {
                    Toast.makeText(getContext(), "Failed to send OTP", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<Void> call, Throwable t) {
                Toast.makeText(getContext(), "Server error", Toast.LENGTH_SHORT).show();
            }
        });
    }

}