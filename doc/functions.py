







def midi_con_setup(dir):
    global midi_outdev_prev, midi_indev_prev

    outtest.configure(state='normal' if midi_outdev else 'disabled')
    panicbtn.configure(state='normal' if midi_outdev else 'disabled')

    for part in [SN1, SN2, AN, DR, FX, ARP, VFX]:
        if part['window']:
            if midi_outdev:
                part['dumpto'].configure(state='normal')
                part['readfrom'].configure(state='normal' if midi_indev else 'disabled')
                if len(part['ldprwgt']) > 1:
                    part['ldprwgt'][1].configure(state='normal' if midi_indev else 'disabled')
            else:
                part['dumpto'].configure(state='disabled')
                part['readfrom'].configure(state='disabled')
                part['storeto'].configure(state='disabled')
                part['ldprwgt'][1].configure(state='disabled')

def noop():
    pass

# call as: unsaved_changes(win, question), returns: Yes/No
def unsaved_changes(win, question):
    rtn = win.message_box(
        title='Unsaved changes',
        icon='question',
        message=f"There are unsaved changes that will be lost unless you save them first.\n\n{question}",
        type='YesNo',
        default='No'
    )
    return rtn

# Confirm store patch in JD-Xi user memory, returns: Yes/No
def store_confirm(win, patchnr):
    rtn = win.message_box(
        title='Confirm Patch Overwrite',
        icon='question',
        message=f"Do you really want to overwrite user patch {patchnr} on your JD-Xi with your current patch?\n",
        type='YesNo',
        default='No'
    )
    return rtn

# Error popup window
def error(win, msg):
    win.message_box(
        title='Error',
        icon='warning',
        message=msg,
        type='Ok',
        default='Ok'
    )

# Success popup window
def success(win, msg):
    win.message_box(
        title='Success',
        icon='info',
        message=msg,
        type='Ok',
        default='Ok'
    )


import tkinter as tk

def top_menubar(win, frame):
    # Pulldown Menus
    pdmenu = tk.Frame(frame)
    pdmenu.pack(side='left')

    btn0 = tk.Menubutton(pdmenu, text='File', tearoff=0, anchor='w')
    btn0.menu = tk.Menu(btn0, tearoff=0)
    btn0.menu.add_command(label='Quit', accelerator='Ctrl+Q', command=lambda: exit_program(win))
    btn0['menu'] = btn0.menu
    btn0.pack(side='left')

    btn1 = tk.Menubutton(pdmenu, text='Edit', tearoff=0, anchor='w')
    btn1.menu = tk.Menu(btn1, tearoff=0)
    btn1.menu.add_command(label='Hide/Show Donate Button', command=lambda: donate.grid_forget() if donate.winfo_ismapped() else donate.grid(**D['GridCfg'], padx=10, pady=5, row=0, column=4))
    btn1.menu.add_checkbutton(label='Automatically Check for Updates', variable=upd_chk, command=save_config)
    btn1.menu.add_separator()
    btn1.menu.add_command(label='Save Settings', command=save_config)
    btn1['menu'] = btn1.menu
    btn1.pack(side='left')

    btn2 = tk.Menubutton(pdmenu, text='Help', tearoff=0, anchor='w')
    btn2.menu = tk.Menu(btn2, tearoff=0)
    btn2.menu.add_command(label='Online Documentation', command=lambda: access_url(f"{webaddr}/docs/?ref={vernr}"))
    btn2.menu.add_command(label='JDXi Manager Website', command=lambda: access_url(f"{webaddr}/?ref={vernr}"))
    btn2.menu.add_command(label='Roland JD-Xi Manuals', command=lambda: access_url(f"{webaddr}/goto/roland_mans?ref={vernr}"))
    btn2.menu.add_separator()
    btn2.menu.add_command(label='About JDXi Manager', command=lambda: about(win))
    btn2['menu'] = btn2.menu
    btn2.pack(side='left')

    # global keyboard bindings for Menus
    win.bind("<Control-q>", lambda event: exit_program(win))
    win.bind("<Control-Q>", lambda event: exit_program(win))



