from textual.theme import Theme

hacker_terminal = Theme(
    name="hacker-terminal",
    primary="#00cc00",      
    secondary="#2EB82E",    
    accent="#1F8F1F",       
    foreground="#33CC33",   
    background="#1E1E1E",   
    surface="#2A2A2A",      
    panel="#333333",        
    success="#33CC33",      
    warning="#88CC88",      
    error="#FF5555",        
    dark=True,
    variables={
        "border": "#33CC33",
        "border-blurred": "#224422",
        "block-cursor-foreground": "#1E1E1E",
        "block-cursor-background": "#33CC33",
        "input-selection-background": "#33CC3340",
        "footer-key-foreground": "#33CC33",
    },
)

cyberpunk_terminal = Theme(
    name="cyberpunk-terminal",
    primary="#FFD700",      
    secondary="#00FFFF",    
    accent="#00FF66",       
    foreground="#FFD700",   
    background="#0A2A3F",
    surface="#164755",
    panel="#205B6B",
    success="#00FF66",
    warning="#FFC600",
    error="#FF3344",

    dark=True,

    variables={
        "border": "#FFD700",
        "border-blurred": "#375E6B",

        "block-cursor-foreground": "#0A2A3F",
        "block-cursor-background": "#FFD700",

        "input-selection-background": "#FFD700",
        "input-selection-foreground": "#000000",

        "selection-background": "#FFD700",
        "selection-foreground": "#000000",

        "footer-key-foreground": "#00FFFF",
    },
)

sunset = Theme(
    name="sunset",
    primary="#FF6E6E",      
    secondary="#FFA36C",    
    accent="#C17BFF",       
    foreground="#FFF1E6",   
    background="#2E1A47",   
    surface="#3A204D",      
    panel="#462859",        
    success="#6EF29C",
    warning="#FFD275",
    error="#FF4E50",
    dark=True,
    variables={
        "border": "#FF6E6E",
        "border-blurred": "#73344D",
        "block-cursor-foreground": "#2E1A47",
        "block-cursor-background": "#FF6E6E",
        "input-selection-background": "#FF6E6E40",
        "footer-key-foreground": "#C17BFF",
    },
)

deep_space = Theme(
    name="deep-space",

    primary="#FF4081",
    secondary="#002233",
    accent="#00D9FF",      
    foreground="#E0E0E0",
    background="#000010",
    surface="#001122",
    panel="#001A33",
    success="#33FFCC",
    warning="#FFEA00",
    error="#FF1744",
    dark=True,
    variables={
        "border": "#FF4081",
        "border-blurred": "#002233",
        "block-cursor-foreground": "#000010",
        "block-cursor-background": "#00D9FF",
        "input-selection-background": "#00D9FF40",
        "footer-key-foreground": "#FF4081",
    },
)

monochrome_minimal = Theme(
    name="monochrome-minimal",
    primary="#FFFFFF",      
    secondary="#EEEEEE",    
    accent="#CCCCCC",       
    foreground="#FFFFFF",   
    background="#000000",   
    surface="#111111",      
    panel="#222222",        
    success="#00FF00",
    warning="#FFFF00",
    error="#FF0000",
    dark=True,
    variables={
        "border": "#FFFFFF",
        "border-blurred": "#444444",
        "block-cursor-foreground": "#000000",
        "block-cursor-background": "#FFFFFF",
        "input-selection-background": "#FFFFFF40",
        "footer-key-foreground": "#EEEEEE",
    },
)

moonstone = Theme(
    name="moonstone",
    primary="#6FA3A3",      
    secondary="#5E7A7A",    
    accent="#A3C4BC",       
    foreground="#E3E3E3",   
    background="#1F2128",   
    surface="#2A2D34",      
    panel="#34384D",        
    success="#8EBF87",
    warning="#D0A15E",
    error="#BF616A",
    dark=True,
    variables={
        "border": "#6FA3A3",
        "border-blurred": "#2F3138",
        "block-cursor-foreground": "#1F2128",
        "block-cursor-background": "#6FA3A3",
        "input-selection-background": "#6FA3A340",
        "footer-key-foreground": "#A3C4BC",
    },
)

ember = Theme(
    name="ember",
    primary="#C57E5A",      
    secondary="#9C5A4E",    
    accent="#DAB985",       
    foreground="#E8E8E8",   
    background="#1E1C1F",   
    surface="#2C2A2D",      
    panel="#353335",        
    success="#8EBF87",
    warning="#D0A15E",
    error="#BF616A",
    dark=True,
    variables={
        "border": "#C57E5A",
        "border-blurred": "#3A383A",
        "block-cursor-foreground": "#1E1C1F",
        "block-cursor-background": "#C57E5A",
        "input-selection-background": "#C57E5A40",
        "footer-key-foreground": "#DAB985",
    },
)

dusk_violet = Theme(
    name="dusk-violet",
    primary="#8A6EA3",      
    secondary="#6E5980",    
    accent="#B39DBF",       
    foreground="#EAE8EE",   
    background="#1D1B23",   
    surface="#2B2930",      
    panel="#33303A",        
    success="#8EBF87",
    warning="#D0A15E",
    error="#BF616A",
    dark=True,
    variables={
        "border": "#8A6EA3",
        "border-blurred": "#3A383F",
        "block-cursor-foreground": "#1D1B23",
        "block-cursor-background": "#8A6EA3",
        "input-selection-background": "#8A6EA340",
        "footer-key-foreground": "#B39DBF",
    },
)
