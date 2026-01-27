package com.example.splitexpense;

import android.content.Intent;
import android.os.Bundle;
import androidx.fragment.app.Fragment;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

public class RegisterFragment extends Fragment {

    EditText et_name, et_address;
    Button btn_register;

    public RegisterFragment() { }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        View view = inflater.inflate(R.layout.fragment_register, container, false);

        et_name = view.findViewById(R.id.et_name);
        et_address = view.findViewById(R.id.et_address);
        btn_register = view.findViewById(R.id.btn_register);

        btn_register.setOnClickListener(v -> {

            String name = et_name.getText().toString().trim();
            String address = et_address.getText().toString().trim();

            if(name.isEmpty()){
                et_name.setError("Enter your name");
                return;
            }

            if(address.isEmpty()){
                et_address.setError("Enter your address");
                return;
            }

            Toast.makeText(getContext(), "Registered Successfully!", Toast.LENGTH_SHORT).show();

            Intent intent = new Intent(getActivity(), MainActivity.class);
            startActivity(intent);

            // 🔹 Close AuthActivity so user can't go back to login
            getActivity().finish();

            // Later → send to backend
            // For now → move to main app screen or finish auth
        });

        return view;
    }
}
