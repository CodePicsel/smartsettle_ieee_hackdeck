package com.example.splitexpense;

import android.os.Bundle;
import android.view.*;
import android.widget.*;
import androidx.fragment.app.Fragment;
import com.example.splitexpense.R;
//import com.example.splitexpense.models.OtpVerifyRequest;
//import com.example.trustlending.network.ApiClient;
//import com.example.trustlending.network.ApiService;
//import retrofit2.*;

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

            // 🔹 TEMP: Assume user not registered
            boolean isUserNew = true;

            if(isUserNew){
                RegisterFragment fragment = new RegisterFragment();

                getParentFragmentManager().beginTransaction()
                        .replace(R.id.auth_fragment_container, fragment)
                        .addToBackStack(null)
                        .commit();
            } else {
                // Existing user → go to MainActivity later
            }
        });

        return view;
    }

    private void verifyOtp() {
        String otp = etOtp.getText().toString().trim();


    }
}
