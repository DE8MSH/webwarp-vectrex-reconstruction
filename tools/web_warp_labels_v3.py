# Web Warp (1983) - corrected Ghidra V3 labels
# Target: Ghidra 12.x Python/PyGhidra script environment.
#
# V3 corrects important semantic mistakes from V2:
#   $0100 = Trophy Room 2 check/bug, NOT bonus life.
#   $0F54 = web-line allocator/spawner, NOT enemy spawn.
#   $0FCE = Capture Rod / creature capture.
#   $1028 = Cosmic Dragon projectile.
#   $1104 = Cosmic Dragon trigger.
#   $C94F = SIX Guardian records.
#   $C9BB = Fantasy Creature record.
#   $CB22 = Trophy Room entrance portal.
#   $C9CD = Cosmic Dragon.
#   $C9F1..$CA41 = nine 9-byte blaster shots.
#
# It only adds/renames symbols/comments. It never patches ROM bytes.

from ghidra.program.model.symbol import SourceType

def A(v):
    return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v)

def safe_label(address, name, comment=""):
    ad = A(address)
    st = currentProgram.getSymbolTable()
    old = st.getPrimarySymbol(ad)
    try:
        if old is None or old.getName().startswith(("FUN_", "DAT_", "UNK_", "LAB_", "SUB_")):
            createLabel(ad, name, True)
        elif old.getName() != name:
            st.createLabel(ad, name, SourceType.USER_DEFINED)
    except Exception as e:
        print("label %04X %s: %s" % (address, name, e))
    if comment:
        try:
            setEOLComment(ad, comment)
        except:
            pass

def safe_func(address, name, comment=""):
    ad = A(address)
    f = getFunctionAt(ad)
    if f is None:
        f = getFunctionContaining(ad)
    if f is None:
        safe_label(address, name, comment)
        return
    try:
        old = f.getName()
        if old.startswith(("FUN_", "SUB_")) or old != name:
            f.setName(name, SourceType.USER_DEFINED)
    except Exception as e:
        print("function %04X %s: %s" % (address, name, e))
    if comment:
        try:
            f.setComment(comment)
        except:
            pass

FUNCS = {
    0x001D: ("WW_CartridgeStart", "Cartridge entry; hidden programmer-credit gate using buttons 1+2+4."),
    0x0040: ("WW_GameInitAndMainLoop", "Initializes gameplay then runs the per-frame main loop."),
    0x00F4: ("WW_CartridgeInit", "Session/menu setup then per-round initialization."),
    0x0100: ("WW_CheckTrophyRoom2", "Original bug: CMPA #$20 (32 decimal) instead of decimal 20."),
    0x011A: ("WW_ShowPlayerTransition", "Shows PLAYER 1/PLAYER 2 transition in alternating two-player mode."),
    0x012E: ("WW_ShowTrophyRoomUntilInput", "Repeatedly renders Trophy Room until button/timer exit."),
    0x0152: ("WW_SetupAndMenu", "Initial 5 lives, player records, bonus pointer, BIOS Select_Game."),
    0x01C6: ("WW_InitRound", "Clears web/object pools and resets per-life state."),
    0x0239: ("WW_InitGameAndWeb", "Builds motion tables, initializes speed/web/player state."),
    0x0362: ("WW_AverageMotionTablePair", "Combines half of two 16-bit motion-table words."),
    0x036F: ("WW_BuildScaledMotionTable", "Expands signed ROM movement bytes into scaled 16-bit RAM tables."),
    0x0393: ("WW_RunStatusScreen", "General PLAYER/GAME OVER/score/high-score status screen loop."),
    0x0437: ("WW_RenderAndAdvanceFrame", "Central vector renderer; also advances depth/lifecycle for several objects."),
    0x08CF: ("WW_DrawTransformedWebVector", "Low-level VIA/DAC web-vector drawing with Rise/Run transforms."),
    0x094F: ("WW_BuildDrawDisplacement", "Builds temporary draw displacement from camera and object coordinates."),
    0x0976: ("WW_AdvanceDepthBySpeed", "8x8->16 multiply; advances object depth using speed/scalar."),
    0x0979: ("WW_AdvanceDepthSignedCore", "Signed add/subtract core used by depth movement."),
    0x099F: ("WW_RenderTrophyRoom", "Draws trophy-room cells and the captured creature vector pairs."),
    0x0A54: ("WW_UpdateCosmicDragon", "Updates Dragon depth and prepares/launches Dragon projectile."),
    0x0AD4: ("WW_DrawDragonAtCurrentState", "Positions/scales Dragon and prepares vector drawing."),
    0x0B14: ("WW_UpdateBonusLifeAndHighScore", "Compares score against ROM thresholds, awards life, updates high score."),
    0x0B3F: ("WW_UpdatePlayerFireAndDeath", "Handles death timeout and Button-4 allocation of one of nine shots."),
    0x0B9A: ("WW_UpdatePlayerMovement", "Joystick speed/lateral movement."),
    0x0BBF: ("WW_UpdatePlayerLateralMotionCore", "Discrete web-sector movement and direction state."),
    0x0C6A: ("WW_SetEntityMotionVector", "Copies a 2-word motion vector into an 18-byte entity."),
    0x0C75: ("WW_TransformAllWorldCoordinates", "Transforms player, six Drones, creature and portal."),
    0x0CC0: ("WW_TransformCoordinate", "Rise/Run fixed-point coordinate rotation."),
    0x0CE1: ("WW_UpdateGuardiansCreaturePortal", "Guardian/creature movement, collisions and Trophy Room transition."),
    0x0F1E: ("WW_TestEntityVsPlayerCollision", "Exact 3-axis threshold collision; returns Carry."),
    0x0F54: ("WW_SpawnWebLine", "Allocates/recycles 3-byte web-line records and updates speed display."),
    0x0FBF: ("WW_UpdatePlayerAngle", "Seven-segment angle lookup ($18BB) + web/camera offset."),
    0x0FCE: ("WW_UpdateCaptureRod", "Button 3, 13-frame rod timer, creature hitbox and 325-point capture."),
    0x1028: ("WW_UpdateDragonShot", "Moves Cosmic Dragon projectile and tests 5x7 hitbox vs Hawk King."),
    0x106A: ("WW_InitWebMotionScript", "Resets camera accumulators and points to $191C motion script."),
    0x1078: ("WW_UpdateWebMotionScript", "Executes repeating 7-byte scripted camera/web-motion records."),
    0x10A9: ("WW_SpawnTrophyRoomPortal", "Spawns CB22 portal after capture at one of seven web positions."),
    0x10D9: ("WW_SwitchPlayer", "Swaps alternating player persistent state and score pointer."),
    0x10F2: ("WW_SelectPlayerSaveArea", "Selects one of the two 4-byte per-player save-state blocks."),
    0x1104: ("WW_TriggerCosmicDragon", "Activates C9CD Dragon state when Vec_Counter_5 reaches 1."),
    0x1CDF: ("WW_ReadJoystickHardware", "Custom VIA joystick sampling routine."),
    0x1D2A: ("WW_UpdateSoundAndMusic", "Music dispatch + 8-slot custom SFX engine."),
}

for address, (name, comment) in FUNCS.items():
    safe_func(address, name, comment)

ROM_DATA = {
    0x0A36: ("WW_Text_TrophyRoom", '"TROPHY ROOM" print record.'),
    0x0A44: ("WW_Text_TrophyRoom2", '"TROPHY ROOM 2" print record.'),
    0x111C: ("WW_VL_TrophyRoomEntrance", "Portal mode-vector list."),
    0x112C: ("WW_VL_PatternXCross", "Patterned X-cross vector list."),
    0x1145: ("WW_DotList_PlayerExplosion", "Player hit/explosion dot list."),
    0x1163: ("WW_ScoreTable", "Words: 75 Drone, 325 creature, 750 Trophy Room entry."),
    0x1169: ("WW_SpeedTextTemplate", 'Display data for "SPEED  10".'),
    0x1177: ("WW_VL_WebSemicircle", "Base web semicircle vector list."),
    0x118F: ("WW_WebLineDelayTable", "Speed-indexed delay/spacing table."),
    0x11A9: ("WW_MotionScaleTable", "16 bytes: 10x4,08x4,04x4,02x4."),
    0x11B9: ("WW_VL_GuardianDrone", "Star/mine vector used for Guardian Drones."),
    0x11D5: ("WW_HiddenProgrammerCredits", "Hidden Print_List text."),
    0x1225: ("WW_TrophyVectorPointerTable", "40 words = 20 species x two animation frames."),
    0x18BB: ("WW_PlayerAngleTable", "Seven signed angles: 17,13,7,0,-7,-13,-17."),
    0x18C2: ("WW_EndDisplayData", '"END" display/list record.'),
    0x18CA: ("WW_Text_Player1", '"PLAYER 1".'),
    0x18D7: ("WW_Text_Player2", '"PLAYER 2".'),
    0x18E4: ("WW_Text_GameOver", '"GAME OVER".'),
    0x18F2: ("WW_BonusThresholdStrings", "25000,50000,100000,250000,500000,999999."),
    0x191C: ("WW_WebMotionScript", "Repeating 7-byte duration/deltaA/deltaB/deltaWeb records."),
    0x1986: ("WW_PlayerVectorPointerTable", "8-frame pointer sequence 0,1,2,3,2,1,0,0."),
    0x1AAE: ("WW_DragonVectorPointerTable", "8-frame Dragon pointer animation."),
    0x1ABE: ("WW_VL_Dragon0", "Cosmic Dragon body frame 0."),
    0x1B01: ("WW_VL_Dragon1", "Cosmic Dragon body frame 1."),
    0x1B44: ("WW_VL_Dragon2", "Cosmic Dragon body frame 2."),
    0x1B87: ("WW_VL_Dragon3", "Cosmic Dragon body frame 3."),
    0x1BCA: ("WW_VL_DragonHead", "Separately rotated Cosmic Dragon head."),
    0x1BD7: ("WW_VL_DragonShot", "Dragon projectile vector list."),
    0x1BE9: ("WW_VL_TrophyRoomHexagon", "Trophy Room cell/window vector."),
    0x1BF7: ("WW_TrophyRoomLayout", "20 placement/scale entries with two frame pointers."),
    0x1C83: ("WW_TrophyRoomEnvelope", "Music envelope."),
    0x1C93: ("WW_Melody_TrophyRoom", "Trophy Room music sequence."),
    0x1CAE: ("WW_VL_XCross", "8-point cross mode-vector list."),
    0x1E79: ("WW_SoundBitMaskTable", "20,10,08,04,02,01."),
    0x1E7F: ("WW_MusicPointerTable", "title, melody2, melody0, melody1 pointers."),
    0x1E87: ("WW_Melody_Title", "Cartridge title/header melody."),
    0x1EA5: ("WW_Melody_0", "Short chirp."),
    0x1EB5: ("WW_Melody_1", "Higher variant of title-like phrase."),
    0x1ED3: ("WW_Melody_2", "Short jingle."),
    0x1EF1: ("WW_SfxJumpDataTable", "8 records x 7 bytes."),
    0x1F29: ("WW_UnusedPromoText", "Unused plaintext promo for Cosmic Chasm / Hyper Chase / Bedlam."),
    0x1FE9: ("WW_RomPadding", "ROM tail/padding."),
}

for address, (name, comment) in ROM_DATA.items():
    safe_label(address, name, comment)

RAM = {
    0xC8BB: ("WW_NextBonusThresholdPtr", "Active player's next bonus-score string pointer."),
    0xC8BD: ("WW_LivesRemaining", "Active player's lives; initialized to 5."),
    0xC8BE: ("WW_TrophyProgress", "Active player's trophy/progression byte; bit7 marks Room 2."),
    0xC89A: ("WW_RequestedSpeed", "Pending/current speed source."),
    0xC89B: ("WW_RequestedWebLineDelay", "Pending speed's web-line delay."),
    0xC89C: ("WW_SpeedChangePending", "Speed update pending flag."),
    0xC89F: ("WW_WebLineSpawnTimer", "Countdown used by $0F54."),
    0xC8A5: ("WW_WebLineDelay", "Current delay between web-line allocations."),
    0xC8B5: ("WW_WebCameraAngleOffset", "Scripted web/camera base angle offset."),
    0xC8CD: ("WW_DragonShotActive", "Cosmic Dragon projectile active/state byte."),
    0xC900: ("WW_WebLine0", "Initial 3-byte moving web-line record."),
    0xC903: ("WW_WebLineFreePool", "Eight additional 3-byte web-line records."),
    0xC94F: ("WW_GuardianPool", "Six 18-byte Guardian Drone records."),
    0xC9BB: ("WW_FantasyCreature", "18-byte current creature record; NOT Guardian #7."),
    0xC9CD: ("WW_CosmicDragon", "Cosmic Dragon state/object record."),
    0xC9DE: ("WW_HawkKing", "Hawk King/player gameplay record."),
    0xC9F0: ("WW_CapturePending", "Nonzero after Capture Rod success; enables portal spawn."),
    0xC9F1: ("WW_ShotPool", "Nine 9-byte blaster-shot records."),
    0xCA42: ("WW_AfterShotPool", "First byte after 9x9-byte shot pool."),
    0xCB22: ("WW_TrophyRoomPortal", "Separate portal record."),
    0xCAD6: ("WW_Player1ScoreState", "Player 1 11-byte score/display structure."),
    0xCAE1: ("WW_Player2ScoreState", "Player 2 11-byte score/display structure."),
}

for address, (name, comment) in RAM.items():
    safe_label(address, name, comment)

# Record boundary labels.
for i, address in enumerate(range(0xC94F, 0xC9BB, 0x12)):
    safe_label(address, "WW_Guardian_%d" % i, "Guardian Drone record %d/5, 18 bytes." % i)

for i, address in enumerate(range(0xC9F1, 0xCA42, 9)):
    safe_label(address, "WW_Shot_%d" % i, "Blaster-shot record %d/8, 9 bytes." % i)

for i, address in enumerate(range(0xC903, 0xC91B, 3), start=1):
    safe_label(address, "WW_WebLine_%d" % i, "Moving/recycled 3-byte web-line record.")

print("Web Warp V3 corrected labels applied.")
print("Important: $0100, $0F54, $0FCE, $1028, $1104 and C9BB/CB22 are corrected from V2.")
