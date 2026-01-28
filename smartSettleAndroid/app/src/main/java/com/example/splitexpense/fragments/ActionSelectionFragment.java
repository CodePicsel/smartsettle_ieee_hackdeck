package com.example.splitexpense.fragments;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;

import androidx.fragment.app.Fragment;

import com.example.splitexpense.R;

public class ActionSelectionFragment extends Fragment {

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        View view = inflater.inflate(R.layout.fragment_action_selection, container, false);

        Button btnLend = view.findViewById(R.id.btnLendMoney);
        Button btnBorrow = view.findViewById(R.id.btnBorrowMoney);

        btnLend.setOnClickListener(v -> openLenderFlow());
        btnBorrow.setOnClickListener(v -> openBorrowerFlow());

        return view;
    }

    private void openLenderFlow() {
        getParentFragmentManager().beginTransaction()
                .replace(R.id.main_fragment_container, new LenderOfferFragment())
                .addToBackStack(null)
                .commit();
    }

    private void openBorrowerFlow() {
        getParentFragmentManager().beginTransaction()
                .replace(R.id.main_fragment_container, new BorrowerHomeFragment())
                .addToBackStack(null)
                .commit();
    }
}
