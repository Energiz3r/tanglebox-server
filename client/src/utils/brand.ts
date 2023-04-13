let style = `text-shadow: 1px 1px 3px black, 2px 2px 2px black, 0 0 4px purple, 2px 2px 4px purple, -2px -2px 4px purple; 
color: rgb(255,0,200); font-weight: 900;  background-image: linear-gradient(to right, rgba(0,0,0,0.1) , rgba(0, 0, 0, 0.2));`;
const brand = String.raw`%c
   __                       .__        ___.                   
 _/  |______    ____   ____ |  |   ____\_ |__   _______  ___  
 \   __\__  \  /    \ / ___\|  | _/ __ \| __ \ /  _ \  \/  /  
  |  |  / __ \|   |  / /_/  |  |_\  ___/| \_\ (  <_> >    <   
  |__| (____  |___|  \___  /|____/\___  |___  /\____/__/\_ \  
            \/     \/_____/ (c) tanglebox.ai\/            \/  
                                                              
`;
export const consoleBranding = () => console.log(brand, style);
