package com.example.myapplication

import android.os.Bundle
import android.util.Log
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.navigation.fragment.findNavController
import kotlinx.android.synthetic.*
import kotlinx.android.synthetic.main.fragment_meetings.*
import kotlinx.android.synthetic.main.fragment_meetings.view.*

class MeetingsFragment : Fragment(R.layout.fragment_meetings) {

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_meetings,container,false)
    }


    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        view.TextViewName.setOnClickListener {
            findNavController().navigate(R.id.action_meetingsFragment_to_eventFragment)
        }

        view.TextViewParticipants.setOnClickListener {
            findNavController().navigate(R.id.action_meetingsFragment_to_participantsFragment)
        }

        view.btnToHistory.setOnClickListener {
            findNavController().navigate(R.id.action_meetingsFragment_to_meetingsHistoryFragment)
        }

        view.btnAdd.setOnClickListener {
            findNavController().navigate(R.id.action_meetingsFragment_to_fragmentAddMeeting)
        }
    }
}