1st Dec 22

* Finished package ready for pipetting settings modulation
* Increased reaction volume to 20ul to account for evaporation in the absence of discontinued wax.

Next steps:

Master Mix Modulation.
Different protein component mixes.


1st Nov 22

* lysate seems fine. No need to further touch those settings
* Substrates missing more wells since I **increased** the volume of the well. Seems unbelievable so I'll run again and watch carefully.

 Notes

 A5 and A6, substrates dispensed on to out side of tip. Realised that the substrates_dispense_well_bottom_clearance: 0.2 whilst lysate_dispense_well_bottom_clearance: 0.1.
 Set substrates_dispense_well_bottom_clearance: 0.1 accordingly reran.

Notes:

It looks like dispensed liquid on the outside of the tip maybe correlated with a slow dispense speed....
it still happens but v rarely and might be to with that...
obvs the dispense speed changes a lot in this doe.

this has really helped. Only 3x missed wells for substrates in the first row. all others fine.

Robot stopped with this error:
`client_loop: send disconnect: Connection reset`
Appears to be an unstable USB SSH connection.

Probably okay to progress as the remaining missed wells maybe a function of pipetting speeds.
