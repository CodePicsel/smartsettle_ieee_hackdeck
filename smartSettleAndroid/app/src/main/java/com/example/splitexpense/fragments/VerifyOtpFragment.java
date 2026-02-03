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
    String tempToken;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Bundle args = getArguments();
        if (args != null) {
            phone = args.getString("phone", "");
            tempToken = args.getString("temp_token", "");
        } else {
            Toast.makeText(getContext(), "Missing phone or token!", Toast.LENGTH_SHORT).show();
            if (getActivity() != null) getActivity().finish();
        }
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
            btnVerifyOtp.setEnabled(false);
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

//                if (!response.isSuccessful()) {
//                    btnVerifyOtp.setEnabled(true); // allow retry
//                    Toast.makeText(getContext(), "Invalid OTP or server error", Toast.LENGTH_SHORT).show();
//                    return;
//                }
//
                VerifyOtpResponse body = response.body();
//                if (body == null) {
//                    Toast.makeText(getContext(), "Empty server response", Toast.LENGTH_SHORT).show();
//                    return;
//                }
                String tokenFromServer = body.getAccessToken(); // token from backend
                if (tokenFromServer == null || tokenFromServer.isEmpty()) {
                    Toast.makeText(getContext(), "Server did not return token", Toast.LENGTH_LONG).show();
                    return;
                }



                if (body.getUser() != null) {
                    // Existing user → go to MainActivity
                    requireActivity()
                            .getSharedPreferences("app_prefs", getContext().MODE_PRIVATE)
                            .edit()
                            .putString("access_token", tokenFromServer)
                            .apply();
                    startActivity(new Intent(getActivity(), MainActivity.class));
                    requireActivity().finish();

                } else {
                    // New user → go to Register screen
                    RegisterFragment fragment = new RegisterFragment();
                    Bundle bundle = new Bundle();
                    bundle.putString("temp_token", tokenFromServer);
                    fragment.setArguments(bundle);
                    getParentFragmentManager().beginTransaction()
                            .replace(R.id.auth_fragment_container, fragment)
                            .addToBackStack(null)
                            .commit();
                    }
            }

            @Override
            public void onFailure(Call<VerifyOtpResponse> call, Throwable t) {
                btnVerifyOtp.setEnabled(true); // allow retry

                Toast.makeText(getContext(), "Server error", Toast.LENGTH_SHORT).show();
            }
        });
    }
}
