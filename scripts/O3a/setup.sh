EVENT_LIST="GW150914 GW151012 GW151226 GW170104 GW170608 GW170729 GW170809 GW170814 GW170818 GW170823 GW190408 GW190412 GW190413A GW190413B GW190421A GW190424A GW190426A GW190503A GW190512A GW190513A GW190514A GW190517A GW190519A GW190521 GW190521A GW190527A GW190602A GW190620A GW190630A GW190701A GW190706A GW190707A GW190708A GW190719A GW190720A GW190727A GW190728A GW190731A GW190803A GW190814 GW190828A GW190828B GW190909A GW190910A GW190915A GW190924A GW190929A GW190930A"
#EVENT_LIST="GW190408 GW190412 GW190413A GW190413B GW190421A GW190424A GW190426A GW190503A GW190512A GW190513A GW190514A GW190517A GW190519A GW190521 GW190521A GW190527A GW190602A GW190620A GW190630A GW190701A GW190706A GW190707A GW190708A GW190719A GW190720A GW190727A GW190728A GW190731A GW190803A GW190814 GW190828A GW190828B GW190909A GW190910A GW190915A GW190924A GW190929A GW190930A"
for EVENT in ${EVENT_LIST}
do
  bilby_pipe ${EVENT}.ini
done
