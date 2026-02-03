package com.example.splitexpense.activities;

import android.os.Bundle;
import androidx.appcompat.app.AppCompatActivity;

import com.example.splitexpense.R;
import com.example.splitexpense.fragments.ActionSelectionFragment;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        if(savedInstanceState == null){
            getSupportFragmentManager().beginTransaction()
                    .replace(R.id.main_fragment_container, new ActionSelectionFragment())
                    .commit();
        }
    }
}
