import streamlit as st
import random

# Configuración de la página web
st.set_page_config(
    page_title="TheVikingsTournament",
    page_icon="⚔️",
    layout="centered"
)

# Estilos CSS con temática vikinga (Oscuro, Dorado y Rojo Sangre)
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: #FFFFFF;
}
h1, h2, h3 {
    color: #D4AF37 !important;
    font-family: 'Georgia', serif;
}
.stButton>button {
    background-color: #8B0000;
    color: white;
    border-radius: 6px;
    font-weight: bold;
    border: 1px solid #D4AF37;
    width: 100%;
}
.stButton>button:hover {
    background-color: #5C0000;
    color: #FFD700;
}
</style>
""", unsafe_allow_html=True)

# ==========================
# INICIALIZACIÓN DE ESTADOS
# ==========================
if "etapa" not in st.session_state:
    st.session_state.etapa = "menu"
if "stats_globales" not in st.session_state:
    st.session_state.stats_globales = {}
if "grupos" not in st.session_state:
    st.session_state.grupos = {}
if "calendario" not in st.session_state:
    st.session_state.calendario = {}
if "fecha_actual" not in st.session_state:
    st.session_state.fecha_actual = 0
if "historial_fases" not in st.session_state:
    st.session_state.historial_fases = []
if "bye_usado" not in st.session_state:
    st.session_state.bye_usado = False
if "tie_data" not in st.session_state:
    st.session_state.tie_data = None
if "tie_resolution" not in st.session_state:
    st.session_state.tie_resolution = None

# ==========================
# FUNCIONES AUXILIARES
# ==========================
def es_mejor(eq1, eq2, stats):
    s1, s2 = stats[eq1], stats[eq2]
    if s1['pts'] != s2['pts']: return s1['pts'] > s2['pts']
    if s1['dif'] != s2['dif']: return s1['dif'] > s2['dif']
    if s1['gf'] != s2['gf']: return s1['gf'] > s2['gf']
    if s1['gc'] != s2['gc']: return s1['gc'] < s2['gc']
    return True

def ordenar_equipos_por_stats(lista_equipos, stats):
    equipos = list(lista_equipos)
    n = len(equipos)
    for i in range(n):
        for j in range(0, n-i-1):
            if not es_mejor(equipos[j], equipos[j+1], stats):
                equipos[j], equipos[j+1] = equipos[j+1], equipos[j]
    return equipos

def generar_calendario(equipos):
    n = len(equipos)
    temp = list(equipos)
    if n % 2 != 0:
        temp.append(None)
        n += 1
    fechas, descansos = [], []
    for i in range(n - 1):
        fecha, descansa = [], None
        for j in range(n // 2):
            eq1, eq2 = temp[j], temp[n - 1 - j]
            if eq1 is None: descansa = eq2
            elif eq2 is None: descansa = eq1
            else: fecha.append((eq1, eq2))
        fechas.append(fecha)
        descansos.append(descansa)
        temp.insert(1, temp.pop())
    return fechas, descansos

# ==========================
# 1. MENÚ PRINCIPAL
# ==========================
if st.session_state.etapa == "menu":
    st.markdown("<h1 style='text-align: center;'>VIKINGS LEAGUE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #A9A9A9;'>TORNEO FINAL - DRAFT</p>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Configurar Nuevo Torneo"):
            st.session_state.etapa = "config"
            st.rerun()

# ==========================
# 2. CONFIGURACIÓN
# ==========================
elif st.session_state.etapa == "config":
    st.markdown("<h2>⚔️ Configuración del Torneo</h2>", unsafe_allow_html=True)
    
    num_grupos = st.selectbox("Cantidad de Grupos (1-4):", [1, 2, 3, 4], index=1)
    num_eq_grupo = st.selectbox("Equipos por Grupo (2-6):", [2, 3, 4, 5, 6], index=2)
    clasif_por_grupo = st.selectbox("Clasificados por Grupo:", [1, 2, 3, 4], index=1)
    tipo_cruce = st.selectbox("Tipo de Emparejamiento (Eliminatorias):", ["Cruces estipulados (Mundial)", "Por bombo", "Al azar"])
    
    if st.button("Continuar a Registro"):
        if clasif_por_grupo >= num_eq_grupo:
            st.error("Los clasificados deben ser menores a la cantidad de equipos por grupo.")
        else:
            st.session_state.num_grupos = num_grupos
            st.session_state.num_eq_grupo = num_eq_grupo
            st.session_state.clasif_por_grupo = clasif_por_grupo
            st.session_state.tipo_cruce = tipo_cruce
            st.session_state.etapa = "registro"
            st.rerun()

# ==========================
# 3. REGISTRO DE EQUIPOS
# ==========================
elif st.session_state.etapa == "registro":
    st.markdown("<h2>🛡️ Registro de Participantes</h2>", unsafe_allow_html=True)
    total = st.session_state.num_grupos * st.session_state.num_eq_grupo
    
    nombres_inputs = []
    with st.form("form_registro"):
        for i in range(total):
            nombres_inputs.append(st.text_input(f"Jugador {i+1}", key=f"eq_{i}"))
        
        btn_generar = st.form_submit_button("Generar Torneo")
        
    if btn_generar:
        equipos = [n.strip() for n in nombres_inputs]
        if "" in equipos or len(set(equipos)) != len(equipos):
            st.error("Llene todos los campos con nombres únicos y sin vacíos.")
        else:
            random.shuffle(equipos)
            st.session_state.grupos = {f"Grupo {chr(65+i)}": equipos[i*st.session_state.num_eq_grupo : (i+1)*st.session_state.num_eq_grupo] for i in range(st.session_state.num_grupos)}
            
            st.session_state.stats_globales = {eq: {'pj': 0, 'v': 0, 'e': 0, 'd': 0, 'pts': 0, 'gf': 0, 'gc': 0, 'dif': 0, 'h2h': {e:0 for e in equipos}} for eq in equipos}
            st.session_state.calendario = {g: generar_calendario(eqs) for g, eqs in st.session_state.grupos.items()}
            
            st.session_state.fecha_actual = 0
            st.session_state.total_fechas = len(st.session_state.calendario[list(st.session_state.grupos.keys())[0]][0])
            st.session_state.historial_fases = []
            st.session_state.bye_usado = False
            st.session_state.etapa = "grupos_jornadas"
            st.rerun()

# ==========================
# 4. FASE DE GRUPOS (JORNADAS)
# ==========================
elif st.session_state.etapa == "grupos_jornadas":
    f_act = st.session_state.fecha_actual
    t_fec = st.session_state.total_fechas
    
    st.markdown(f"<h2>Fase de Grupos - Fecha {f_act + 1} de {t_fec}</h2>", unsafe_allow_html=True)
    
    # Acordeón o Expander para ver posiciones parciales
    with st.expander("📊 Ver Posiciones Parciales en Vivo"):
        for g_name, eqs in st.session_state.grupos.items():
            st.markdown(f"**{g_name}**")
            ord_eqs = ordenar_equipos_por_stats(eqs, st.session_state.stats_globales)
            data_tabla = []
            for eq in ord_eqs:
                st_eq = st.session_state.stats_globales[eq]
                data_tabla.append({"Equipo": eq, "PJ": st_eq['pj'], "V": st_eq['v'], "E": st_eq['e'], "D": st_eq['d'], "GF": st_eq['gf'], "GC": st_eq['gc'], "DIF": st_eq['dif'], "PTS": st_eq['pts']})
            st.dataframe(data_tabla, hide_index=True)

    with st.form("form_jornada"):
        resultados_inputs = []
        for nombre_grupo, (fechas_grupo, descansos_grupo) in st.session_state.calendario.items():
            st.markdown(f"### {nombre_grupo}")
            descansa = descansos_grupo[f_act]
            if descansa:
                st.caption(f"😴 Descansa: {descansa}")
                
            for eq1, eq2 in fechas_grupo[f_act]:
                col1, col2, col3, col4, col5 = st.columns([3, 1, 0.5, 1, 3])
                with col1:
                    st.markdown(f"<div style='text-align: right; padding-top: 8px;'>{eq1}</div>", unsafe_allow_html=True)
                with col2:
                    g1 = st.text_input("g1", value="0", key=f"{nombre_grupo}_{eq1}_{eq2}_1", label_visibility="collapsed")
                with col3:
                    st.markdown("<div style='text-align: center; padding-top: 8px;'>-</div>", unsafe_allow_html=True)
                with col4:
                    g2 = st.text_input("g2", value="0", key=f"{nombre_grupo}_{eq1}_{eq2}_2", label_visibility="collapsed")
                with col5:
                    st.markdown(f"<div style='text-align: left; padding-top: 8px;'>{eq2}</div>", unsafe_allow_html=True)
                resultados_inputs.append((eq1, eq2, g1, g2))
                
        txt_btn = "Guardar y Siguiente Fecha" if f_act < t_fec - 1 else "Finalizar Fase de Grupos"
        submitted = st.form_submit_button(txt_btn)
        
    if submitted:
        try:
            parsed_res = [(eq1, eq2, int(g1), int(g2)) for eq1, eq2, g1, g2 in resultados_inputs]
        except ValueError:
            st.error("Por favor ingrese valores numéricos válidos en los marcadores.")
            st.stop()
            
        for eq1, eq2, g1, g2 in parsed_res:
            st1 = st.session_state.stats_globales[eq1]
            st2 = st.session_state.stats_globales[eq2]
            
            st1['pj'] += 1; st2['pj'] += 1
            st1['gf'] += g1; st1['gc'] += g2; st1['dif'] = st1['gf'] - st1['gc']
            st2['gf'] += g2; st2['gc'] += g1; st2['dif'] = st2['gf'] - st2['gc']
            
            if g1 > g2:
                st1['pts'] += 3; st1['v'] += 1; st2['d'] += 1
            elif g2 > g1:
                st2['pts'] += 3; st2['v'] += 1; st1['d'] += 1
            else:
                st1['pts'] += 1; st2['pts'] += 1
                st1['e'] += 1; st2['e'] += 1
                
        st.session_state.fecha_actual += 1
        if st.session_state.fecha_actual < st.session_state.total_fechas:
            st.rerun()
        else:
            st.session_state.etapa = "posiciones_finales"
            st.rerun()

# ==========================
# 5. POSICIONES FINALES DE GRUPOS
# ==========================
elif st.session_state.etapa == "posiciones_finales":
    st.markdown("<h2>Posiciones Finales - Fase de Grupos</h2>", unsafe_allow_html=True)
    
    st.session_state.clasificados_por_grupo = {}
    st.session_state.clasificados_globales = []
    
    for nombre_grupo, equipos in st.session_state.grupos.items():
        st.markdown(f"### {nombre_grupo}")
        equipos_ord = ordenar_equipos_por_stats(equipos, st.session_state.stats_globales)
        st.session_state.grupos[nombre_grupo] = equipos_ord
        
        data_tabla = []
        clasificados_grupo = []
        for i, eq in enumerate(equipos_ord):
            st_eq = st.session_state.stats_globales[eq]
            estado = "✔️ Clasifica" if i < st.session_state.clasif_por_grupo else "❌ Eliminado"
            data_tabla.append({
                "Pos": i+1, "Equipo": eq, "PJ": st_eq['pj'], "V": st_eq['v'], 
                "E": st_eq['e'], "D": st_eq['d'], "GF": st_eq['gf'], "GC": st_eq['gc'], 
                "DIF": st_eq['dif'], "PTS": st_eq['pts'], "Estado": estado
            })
            if i < st.session_state.clasif_por_grupo:
                st.session_state.clasificados_globales.append(eq)
                clasificados_grupo.append(eq)
                
        st.session_state.clasificados_por_grupo[nombre_grupo] = clasificados_grupo
        st.dataframe(data_tabla, hide_index=True)
        
    if st.button("Avanzar a Eliminatorias"):
        # Preparar eliminatorias iniciales
        parejas = []
        clasificados = list(st.session_state.clasificados_globales)
        
        if len(clasificados) % 2 != 0 and not st.session_state.bye_usado:
            candidatos = ordenar_equipos_por_stats(clasificados, st.session_state.stats_globales)
            mejor_bye = candidatos[0]
            parejas.append((mejor_bye, None))
            clasificados.remove(mejor_bye)
            st.session_state.bye_usado = True
            
        tipo_cruce = st.session_state.tipo_cruce
        num_grp = st.session_state.num_grupos
        clas_grp = st.session_state.clasif_por_grupo
        
        if tipo_cruce == "Cruces estipulados (Mundial)" and num_grp >= 2 and clas_grp >= 2 and len(parejas) == 0:
            g_keys = list(st.session_state.grupos.keys())
            primeros = [st.session_state.clasificados_por_grupo[g][0] for g in g_keys]
            segundos = [st.session_state.clasificados_por_grupo[g][1] for g in g_keys]
            for i in range(len(g_keys)):
                parejas.append((primeros[i], segundos[(i + 1) % len(g_keys)]))
            sobrantes = [eq for eq in clasificados if eq not in [e for p in parejas for e in p]]
            random.shuffle(sobrantes)
            for i in range(0, len(sobrantes), 2):
                if i + 1 < len(sobrantes): parejas.append((sobrantes[i], sobrantes[i+1]))
        elif tipo_cruce == "Por bombo" and clas_grp >= 2 and len(parejas) == 0:
            g_keys = list(st.session_state.grupos.keys())
            bombo1 = [st.session_state.clasificados_por_grupo[g][0] for g in g_keys]
            bombo2 = [st.session_state.clasificados_por_grupo[g][1] for g in g_keys]
            random.shuffle(bombo2)
            for i in range(len(bombo1)):
                parejas.append((bombo1[i], bombo2[i]))
            sobrantes = [eq for eq in clasificados if eq not in bombo1 and eq not in bombo2]
            random.shuffle(sobrantes)
            for i in range(0, len(sobrantes), 2):
                if i + 1 < len(sobrantes): parejas.append((sobrantes[i], sobrantes[i+1]))
        else:
            random.shuffle(clasificados)
            for i in range(0, len(clasificados), 2):
                if i + 1 < len(clasificados): parejas.append((clasificados[i], clasificados[i+1]))
                
        st.session_state.enfrentamientos_actuales = parejas
        st.session_state.etapa = "eliminatorias"
        st.rerun()

# ==========================
# 6. FASE ELIMINATORIA
# ==========================
elif st.session_state.etapa == "eliminatorias":
    total_vivos = len(st.session_state.enfrentamientos_actuales) * 2
    ronda_nombre = "ELIMINATORIAS"
    if total_vivos <= 8 and total_vivos > 4: ronda_nombre = "CUARTOS"
    elif total_vivos <= 4 and total_vivos > 2: ronda_nombre = "SEMIFINAL"
    elif total_vivos <= 2: ronda_nombre = "GRAN FINAL"
    
    st.markdown(f"<h2>⚔️ {ronda_nombre} (Ida y Vuelta) ⚔️</h2>", unsafe_allow_html=True)
    
    # Resolver empate si hay alguno pendiente
    if st.session_state.tie_data is not None:
        eq1, eq2, total1, total2 = st.session_state.tie_data
        st.warning(f"¡Empate global ({total1} - {total2}) entre {eq1} y {eq2}!")
        metodo = st.radio("Seleccione método de desempate:", ["Tercer Partido", "Tanda de Penales"], key="radio_tie")
        
        if metodo == "Tercer Partido":
            col_t1, col_t2 = st.columns(2)
            with col_t1: t_g1 = st.text_input(f"Goles {eq1} (3er Pcial)", value="0")
            with col_t2: t_g2 = st.text_input(f"Goles {eq2} (3er Pcial)", value="0")
            if st.button("Confirmar Tercer Partido"):
                try:
                    tg1, tg2 = int(t_g1), int(t_g2)
                    if tg1 == tg2:
                        st.error("En el tercer partido no puede haber empate.")
                    else:
                        ganador = eq1 if tg1 > tg2 else eq2
                        st.session_state.tie_resolution = ganador
                        st.session_state.tie_data = None
                        st.rerun()
                except ValueError:
                    st.error("Ingrese números válidos.")
        else:
            col_p1, col_p2 = st.columns(2)
            with col_p1: p_g1 = st.text_input(f"Penales {eq1}", value="0")
            with col_p2: p_g2 = st.text_input(f"Penales {eq2}", value="0")
            if st.button("Confirmar Penales"):
                try:
                    pg1, pg2 = int(p_g1), int(p_g2)
                    if pg1 == pg2:
                        st.error("En penales debe haber un ganador.")
                    else:
                        ganador = eq1 if pg1 > pg2 else eq2
                        st.session_state.tie_resolution = ganador
                        st.session_state.tie_data = None
                        st.rerun()
                except ValueError:
                    st.error("Ingrese números válidos.")
        st.stop()

    with st.form("form_eliminatorias"):
        eliminatoria_inputs = []
        for idx, (eq1, eq2) in enumerate(st.session_state.enfrentamientos_actuales):
            if eq2 is None:
                st.info(f"👑 ¡Pase Directo! {eq1} avanza automáticamente por rendimiento.")
                eliminatoria_inputs.append((eq1, None, None, None, None, None))
                continue
                
            st.markdown(f"**{eq1} vs {eq2}**")
            c1, c2, c3, c4 = st.columns(4)
            with c1: i1 = st.text_input(f"Ida {eq1}", value="0", key=f"el_{idx}_i1")
            with c2: i2 = st.text_input(f"Ida {eq2}", value="0", key=f"el_{idx}_i2")
            with c3: v2 = st.text_input(f"Vta {eq2}", value="0", key=f"el_{idx}_v2") # Local en vuelta
            with c4: v1 = st.text_input(f"Vta {eq1}", value="0", key=f"el_{idx}_v1")
            
            eliminatoria_inputs.append((eq1, eq2, i1, i2, v1, v2))
            st.write("---")
            
        btn_conf_el = st.form_submit_button("Confirmar Resultados de la Serie")
        
    if btn_conf_el:
        siguientes = []
        resultados_str = []
        
        for eq1, eq2, i1, i2, v1, v2 in eliminatoria_inputs:
            if eq2 is None:
                siguientes.append(eq1)
                resultados_str.append(f"• {eq1} avanzó directo (Rendimiento)")
                continue
                
            try:
                gi1, gi2 = int(i1), int(i2)
                gv1, gv2 = int(v1), int(v2)
                tot1 = gi1 + gv1
                tot2 = gi2 + gv2
                
                if tot1 > tot2:
                    siguientes.append(eq1)
                    resultados_str.append(f"• {eq1} vs {eq2} → {tot1}-{tot2}")
                elif tot2 > tot1:
                    siguientes.append(eq2)
                    resultados_str.append(f"• {eq1} vs {eq2} → {tot1}-{tot2}")
                else:
                    # Guardamos datos para activar la sección de desempate en la siguiente ejecución
                    st.session_state.tie_data = (eq1, eq2, tot1, tot2)
                    st.rerun()
            except ValueError:
                st.error("Ingrese valores numéricos en todas las casillas.")
                st.stop()
                
        # Si hubo resolución de empate previa guardada en sesión
        if st.session_state.tie_resolution:
            ganador = st.session_state.tie_resolution
            # Identificar perdedor para el reporte
            st.session_state.tie_resolution = None
            
        st.session_state.historial_fases.append({"fase": ronda_nombre, "resultados": resultados_str})
        
        if len(siguientes) == 1:
            st.session_state.campeon = siguientes[0]
            st.session_state.etapa = "resumen"
            st.rerun()
        else:
            nuevas_parejas = []
            eqs_av = list(siguientes)
            random.shuffle(eqs_av)
            for i in range(0, len(eqs_av), 2):
                if i + 1 < len(eqs_av):
                    nuevas_parejas.append((eqs_av[i], eqs_av[i+1]))
            st.session_state.enfrentamientos_actuales = nuevas_parejas
            st.rerun()

# ==========================
# 7. RESUMEN DEL TORNEO
# ==========================
elif st.session_state.etapa == "resumen":
    st.markdown("<h1 style='text-align: center;'>VIKINGS LEAGUE</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #A9A9A9;'>RESUMEN DEL TORNEO FINAL</h3>", unsafe_allow_html=True)
    st.write("---")
    
    col_izq = st.container()
    with st.expander("🛡️ Ver Todos los Participantes", expanded=True):
        for eq in st.session_state.stats_globales.keys():
            marc = "👑" if eq == st.session_state.campeon else "🛡️"
            st.write(f"{marc} **{eq}**")
            
    st.markdown("### ⚔️ Resultados por Fases")
    for fase in st.session_state.historial_fases:
        st.markdown(f"**{fase['fase']}**")
        for res in fase['resultados']:
            st.text(res)
            
    st.write("---")
    st.markdown(f"<div style='background-color: #1A1D24; padding: 20px; border-radius: 10px; border: 2px solid #D4AF37; text-align: center;'><h2>👑 CAMPEÓN: {st.session_state.campeon.upper()} 👑</h2></div>", unsafe_allow_html=True)
    
    if st.button("Reiniciar / Nuevo Torneo"):
        st.session_state.etapa = "menu"
        st.rerun()
