package com.example.splitexpense.fragments;

import android.os.Bundle;
import android.view.*;
import android.widget.*;
import androidx.fragment.app.Fragment;
import com.example.splitexpense.R;
import android.content.Intent;
import android.widget.Toast;

import com.example.splitexpense.activities.MainActivity;
import com.example.splitexpense.models.VerifyOtpRequest;
import com.example.splitexpense.models.VerifyOtpResponse;
import com.example.splitexpense.network.ApiClient;
import com.example.splitexpense.network.ApiService;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;


public class VerifyOtpFragment extends Fragment {

    EditText etOtp;
    Button btnVerifyOtp;
    String phone;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        phone = getArguments().getString("phone");
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_verify_otp, container, false);

        etOtp = view.findViewById(R.id.etOtp);
        btnVerifyOtp = view.findViewById(R.id.btnVerifyOtp);

        btnVerifyOtp.setOnClickListener(v -> {

            String otp = etOtp.getText().toString().trim();

            if(otp.length() < 6){
                etOtp.setError("Enter valid OTP");
                return;
            }

            verifyOtpWithBackend(phone, otp);
        });

        return view;
    }

    private void verifyOtp() {
        String otp = etOtp.getText().toString().trim();


    }
    private void verifyOtpWithBackend(String phone, String otp) {

        ApiService apiService = ApiClient.getClient().create(ApiService.class);
        VerifyOtpRequest request = new VerifyOtpRequest(phone, otp);

        apiService.verifyOtp(request).enqueue(new Callback<VerifyOtpResponse>() {
            @Override
            public void onResponse(Call<VerifyOtpResponse> call, Response<VerifyOtpResponse> response) {

                if (response.isSuccessful() && response.body() != null) {

                    VerifyOtpResponse body = response.body();

                    if (body.getUser() != null && body.getUser().getName() != null) {
                        // Existing user → go to MainActivity
                        Intent intent = new Intent(getActivity(), MainActivity.class);
                        startActivity(intent);
                        getActivity().finish();

                    } else {
                        // New user → go to Register screen
                        RegisterFragment fragment = new RegisterFragment();
                        getParentFragmentManager().beginTransaction()
                                .replace(R.id.auth_fragment_container, fragment)
                                .addToBackStack(null)
                                .commit();
                    }

                } else {
                    Toast.makeText(getContext(), "Invalid OTP", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void onFailure(Call<VerifyOtpResponse> call, Throwable t) {
                Toast.makeText(getContext(), "Server error", Toast.LENGTH_SHORT).show();
            }
        });
    }
}
